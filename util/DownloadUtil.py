# -*- coding: utf-8 -*-
"""
文件下载工具类

提供统一的文件下载功能，支持：
- 断点续传
- 失败重试
- 下载进度条显示
- MD5 校验
"""

import os
import requests
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_fixed
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from util.AtomicCounter import AtomicCounter

class DownloadUtil:
    """
    封装常用的文件下载功能，适用于模型文件、资源包等大文件下载场景。
    支持断点续传、失败自动重试、下载进度可视化等功能。
    """

    def __init__(self, max_retries=3, retry_wait=5, chunk_size=1024 * 1024):
        """
        初始化下载工具类

        :param max_retries: 最大重试次数，默认为3次
        :param retry_wait: 每次重试之间的等待时间（秒），默认5秒
        :param chunk_size: 下载块大小（字节），默认1MB
        """
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.chunk_size = chunk_size
        self.logger = logging.getLogger()

    def download_file(self, url, path):
        """
        下载文件并保存到指定路径，支持断点续传

        :param url: 要下载的文件 URL
        :param path: 本地保存路径（含文件名）
        """
        self.logger.info(f"准备下载文件：{url} 至 {path}")

        # 创建目标目录（如果不存在）
        os.makedirs(os.path.dirname(path), exist_ok=True)

        temp_file = path + ".tmp"
        mode = 'ab' if os.path.exists(temp_file) else 'wb'
        headers = {}

        downloaded_size = 0
        if os.path.exists(temp_file):
            downloaded_size = os.path.getsize(temp_file)
            headers['Range'] = f'bytes={downloaded_size}-'

        @retry(stop=stop_after_attempt(self.max_retries), wait=wait_fixed(self.retry_wait))
        def do_download():
            """
            实际执行下载的方法，使用装饰器添加重试机制
            """
            with requests.get(url, stream=True, headers=headers, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('Content-Length', 0)) + downloaded_size

                with open(temp_file, mode) as f, tqdm(
                        desc=os.path.basename(path),
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        initial=downloaded_size,
                        colour='green'
                ) as bar:
                    for chunk in r.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

            # 下载完成后重命名临时文件为目标文件
            if os.path.exists(temp_file):
                os.rename(temp_file, path)
            self.logger.info("✅ 下载完成")

        try:
            do_download()
        except Exception as e:
            self.logger.error(f"❌ 下载失败: {e}")
            raise

    def verify_md5(self, file_path, expected_md5=None):
        """
        校验文件 MD5 值是否与预期一致

        :param file_path: 本地文件路径
        :param expected_md5: 预期的 MD5 字符串
        :return: True if match，False otherwise
        """
        calculated_md5 = self.calculate_md5(file_path)
        if expected_md5:
            return calculated_md5 == expected_md5
        return calculated_md5

    def calculate_md5(self, file_path):
        """
        计算指定文件的 MD5 值

        :param file_path: 文件路径
        :return: MD5 字符串
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_remote_file_size(self, url):
        """
        获取远程文件的 Content-Length

        :param url: 文件地址
        :return: 文件大小（字节）或 None
        """
        try:
            with requests.head(url, timeout=10) as r:
                r.raise_for_status()
                return int(r.headers.get('Content-Length', 0))
        except Exception as e:
            self.logger.warning(f"无法获取远程文件大小: {e}")
            return None

    def is_file_exists_and_valid(self, path, expected_md5=None):
        """
        判断本地文件是否存在且内容有效

        :param path: 文件路径
        :param expected_md5: 可选，预期的 MD5 值
        :return: bool
        """
        if not os.path.exists(path):
            return False
        if expected_md5:
            return self.verify_md5(path, expected_md5)
        return True

    def download_file_multi_threaded(self, url, path, num_threads=4):
        self.logger.info(f"【多线程下载】准备下载文件：{url} 至 {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        total_size = self.get_remote_file_size(url)
        if not total_size:
            self.logger.warning("无法获取文件大小，切换为单线程下载")
            self.download_file(url, path)
            return

        temp_file = path + ".tmp"
        part_files = [f"{temp_file}.part{i}" for i in range(num_threads)]
        ranges = self._split_ranges(total_size, num_threads)

        # 初始化全局进度条和计数器
        progress_bar = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc="整体进度",
            position=0,
            leave=True,
            colour='blue'
        )
        counter = AtomicCounter(0)

        def task(i, start, end):
            self._download_segment(start, end, url, part_files[i], i, total_size, progress_bar, counter)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(task, i, start, end)
                for i, (start, end) in enumerate(ranges)
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"❌ 分片下载异常: {e}")
                    raise

        progress_bar.close()
        self._merge_parts(part_files, path)
        self.logger.info("✅ 多线程下载完成，并已合并文件")

    def _split_ranges(self, total_size, num_parts):
        """
        将文件大小均分，生成 byte-range 列表

        :param total_size: 文件总大小（字节）
        :param num_parts: 分片数
        :return: list of tuples [(start, end), ...]
        """
        part_size = total_size // num_parts
        ranges = []

        for i in range(num_parts):
            start = i * part_size
            end = (start + part_size - 1) if i < num_parts - 1 else total_size - 1
            ranges.append((start, end))

        return ranges

    def _download_segment(self, start_byte, end_byte, url, part_file, part_num, total_size, progress_bar, counter):
        """
        下载指定范围的文件内容，并更新全局进度条

        :param start_byte: 开始位置
        :param end_byte: 结束位置
        :param url: 文件地址
        :param part_file: 临时文件路径
        :param part_num: 分片编号
        :param total_size: 文件总大小
        :param progress_bar: 全局进度条对象
        :param counter: 原子计数器
        """
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}

        downloaded = 0
        if os.path.exists(part_file):
            downloaded = os.path.getsize(part_file)
            counter.add(downloaded)
            progress_bar.update(downloaded)
            if downloaded == end_byte - start_byte + 1:
                self.logger.info(f"【分片 {part_num}】文件已存在，跳过下载")
                return

        with requests.get(url, stream=True, headers=headers, timeout=30) as r:
            r.raise_for_status()
            with open(part_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        chunk_len = len(chunk)
                        counter.add(chunk_len)
                        progress_bar.update(chunk_len)

        self.logger.info(f"【分片 {part_num}】下载完成: {start_byte}-{end_byte}")

    def _merge_parts(self, part_files, final_path):
        """
        合并所有分片文件为完整文件

        :param part_files: 所有分片文件路径列表
        :param final_path: 最终输出路径
        """
        with open(final_path, 'wb') as final_file:
            for idx, part_file in enumerate(part_files):
                self.logger.info(f"正在合并分片 {idx + 1}/{len(part_files)}: {part_file}")
                with open(part_file, 'rb') as pf:
                    while True:
                        chunk = pf.read(1024 * 1024)
                        if not chunk:
                            break
                        final_file.write(chunk)
                os.remove(part_file)  # 删除临时分片文件
        self.logger.info("✅ 所有分片已合并")

