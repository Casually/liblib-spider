import unittest
import time

from util.SQLiteDB import SQLiteDB
from util.DownloadUtil import DownloadUtil
from util.file_util import file_util


def test_db():
    db = SQLiteDB()
    db.init_db()
    db.insert_model_info(time.time(), model_info='{"da":1}')


def test_download():
    config = file_util.read_yml()
    downloader = DownloadUtil(max_retries=3, retry_wait=5)
    downloader.download_file(
        "https://liblibai-online.liblib.cloud/web/model/e98e107e454846a592baa34b93169bf3/70f6dc65c62dc65ffb2832bee5cd45a9933a050f54a66eedd6c77bc83dc3d676.safetensors?auth_key=1748864378-013edbe4e4354371a43ac079d3ad6d4f-0-9aa3b78a8b2b635ad702251673172c14&attname=FLUX%E6%83%85%E8%B6%A3%E5%86%85%E8%A1%A3_%E6%80%A7%E6%84%9F%E7%BD%91%E7%BA%B1%E8%95%BE%E4%B8%9D%E9%9C%B2%E5%8D%8A%E7%90%83%E9%80%8F%E8%A7%86%E5%90%8A%E5%B8%A6%E8%A3%99_%E6%80%A7%E6%84%9F%E7%BD%91%E7%BA%B1%E9%9C%B2%E5%8D%8A%E7%90%83%E8%95%BE%E4%B8%9D%E9%80%8F%E8%A7%86%E5%90%8A%E5%B8%A6%E8%A3%99.safetensors",
        config.get("download")[
            'model_parent_path'] + "/FLUX情趣内衣_性感网纱蕾丝露半球透视吊带裙_性感网纱露半球蕾丝透视吊带裙.safetensors")


def test_download_multi_thread():
    config = file_util.read_yml()
    downloader = DownloadUtil(max_retries=3, retry_wait=5)

    # 单线程下载
    # downloader.download_file('https://example.com/file.zip', '/data/models/file.zip')

    # 多线程下载
    downloader.download_file_multi_threaded(
        url='https://liblibai-online.liblib.cloud/web/model/e98e107e454846a592baa34b93169bf3/70f6dc65c62dc65ffb2832bee5cd45a9933a050f54a66eedd6c77bc83dc3d676.safetensors?auth_key=1748864378-013edbe4e4354371a43ac079d3ad6d4f-0-9aa3b78a8b2b635ad702251673172c14&attname=FLUX%E6%83%85%E8%B6%A3%E5%86%85%E8%A1%A3_%E6%80%A7%E6%84%9F%E7%BD%91%E7%BA%B1%E8%95%BE%E4%B8%9D%E9%9C%B2%E5%8D%8A%E7%90%83%E9%80%8F%E8%A7%86%E5%90%8A%E5%B8%A6%E8%A3%99_%E6%80%A7%E6%84%9F%E7%BD%91%E7%BA%B1%E9%9C%B2%E5%8D%8A%E7%90%83%E8%95%BE%E4%B8%9D%E9%80%8F%E8%A7%86%E5%90%8A%E5%B8%A6%E8%A3%99.safetensors',
        path=config.get("download")[
                 'model_parent_path'] + '/FLUX情趣内衣_性感网纱蕾丝露半球透视吊带裙_性感网纱露半球蕾丝透视吊带裙.safetensors',
        num_threads=1
    )


def read_conf():
    config = file_util.read_yml()
    print(config.get('download')['three_number'])


if __name__ == '__main__':
    # test_db()
    # test_download()
    # test_download_multi_thread()
    read_conf()
