# -*- coding: utf-8 -*-

import requests
import json
import time
from urllib.parse import urlparse, parse_qs
import os
import yaml
import subprocess
import logging

from ModelType import ModelType
from BaseModelType import BaseModelType
from util.file_util import file_util
from util.SQLiteDB import SQLiteDB
from logging.handlers import TimedRotatingFileHandler

db = SQLiteDB()
db.init_db()

# 获取 TOKEN
TOKEN = None
CID = None
autoDownload = None
# 模型存放父级路径，这可以修改，也可以修改ModelType中文件路径
model_file_parent_dir = None
baseUrl = 'https://api2.liblib.art/api/www'
# 搜索模型列表
searchModels = "/model/search"
# 获取模型详情
getModelInfo = "/model/getByUuid/"
# 推荐模型
recommendModels = "/model-version/modelVersion/listByIds"
# 校验下载地址
checkDownloadUrl = "/community/downloadCheck"
# 获取下载地址
getDownloadUrl = "/model/download/"

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 按天切割，保留 7 天
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# 搜索模型列表
def search_model(keyword, types=[], models=[], vipType=[]):
    '''

    :param keyword: 搜索内容
    :param types:  搜索的基模类型
        1 基础算法 v1.5
        2 基础算法 v2.1
        3 基础算法 XL
        7 基础算法 v3
        9 PixArt Σ
        10 Pony
        12 混元DiT v1.1
        13 PixArt α
        19 基础算法 F.1
        20 基础算法 v3.5M
        21 基础算法 v3.5L
    :param models: 模型类型
        1 Checkpoint
        2 Textual Inversion
        3 Hypernetwork
        4 Aesthetic Gradient
        5 LoRA
        6 LyCORIS
        7 Controlnet
        8 Poses
        9 Wildcards
        10 Other
    :param vipType: 会员专属
        0 免费模型
        1 会员专属
        2 仅会员可下载
    :return:
    '''
    logging.info("全量获取数据中，请等待...")

    bodys = {
        'keyword': keyword,
        'periodTime': ["all"],
        'page': 1,
        'pageSize': 50,
        'types': types,
        'models': models,
        'vipType': vipType,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }

    datas = []

    while True:
        logging.info("正在获取第 " + str(bodys["page"]) + " 页数据...")
        time.sleep(1)
        params = {
            'timestamp': time.time()
        }
        response = requests.post(baseUrl + searchModels, params=params, json=bodys, headers=headers)
        json_data = response.json()
        bodys["page"] = bodys["page"] + 1
        # logging.info(json.dumps(json_data, ensure_ascii=False))
        if not json_data["data"]["hasMore"]:
            break
        else:
            # logging.info(json.dumps(json_data.json(), ensure_ascii=False))
            # 将数组存放到 数组中
            for item in json_data["data"]["data"]:
                datas.append(item['uuid'])
    logging.info("获取数据完成，共有 " + str(len(datas)) + " 条数据")
    return datas


# 获取模型详情
def get_model_info(model_id):
    if model_id is None:
        return None
    '''
    :param model_id:
    :return:
    modelType:
        1 Checkpoint
        2 Textual Inversion
        3 Hypernetwork
        4 Aesthetic Gradient
        5 LoRA
        6 LyCORIS
        7 Controlnet
        8 Poses
        9 Wildcards
        10 Other
    '''
    params = {
        'timestamp': time.time()
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }
    res = requests.post(baseUrl + getModelInfo + model_id, params=params, headers=headers)
    # logging.info(json.dumps(res.json(), ensure_ascii=False))
    if res.json()["code"] == 0:
        return res.json()["data"]
    else:
        return None


# 获取搭配模型
def get_recommend_model(versionIds):
    params = {
        'timestamp': time.time()
    }
    bodys = {
        'versionIds': versionIds
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }
    res = requests.post(baseUrl + recommendModels, json=bodys, params=params, headers=headers)
    # 打印双引号json
    # logging.info(json.dumps(res.json(), ensure_ascii=False))
    return res.json()


# 获取下载地址
def get_download_url(model_uuid, model_url):
    params = url_params_to_json(model_url)
    params['timestamp'] = time.time()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        'token': TOKEN
    }
    # logging.info(json.dumps(params, ensure_ascii=False))
    res = requests.get(baseUrl + getDownloadUrl + model_uuid, params=params, headers=headers)
    # logging.info(json.dumps(res.json(), ensure_ascii=False))
    if res.json()["code"] == 0:
        return res.json()["data"]
    else:
        if res.json()["msg"] == '下载超过限制':
            logging.warning("下载超过限制，请更换账号TOKEN后重新下载")
            exit()
        return res.json()["msg"]
    return None


# 校验下载
def get_check_download(model_id, model_name, model_version_id, model_url, model_uuid):
    params = {
        'timestamp': time.time()
    }
    bodys = {
        "cid": CID,
        'modelId': model_id,
        'modelName': model_name,
        'modelVersionId': model_version_id,
        'url': model_url,
        'uuid': model_uuid,
    }
    # logging.info(json.dumps(bodys, ensure_ascii=False))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }
    res = requests.post(baseUrl + checkDownloadUrl, json=bodys, params=params, headers=headers)
    # logging.info(json.dumps(res.json(), ensure_ascii=False))
    return res.json()["data"]


def url_params_to_json(url):
    # 解析 URL
    parsed_url = urlparse(url)

    # 提取查询参数
    params_dict = parse_qs(parsed_url.query)

    # 将参数字典转换为 JSON 对象
    params_json = {k: v[0] for k, v in params_dict.items()}
    return params_json


# 获取文件后缀
def get_url_suffix(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    # 获取文件扩展名（包含点号）
    ext = os.path.splitext(path)[1]
    return ext


# 通过链接获取模型ID
def get_model_id_by_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.rfind('/') != -1:
        return path[path.rfind('/') + 1:]
    if len(path) == 32:
        return path
    logging.warning("无法获取模型编号")
    return None


# 获取配套模型
def get_compatible_model(versionIds=[]):
    if len(versionIds) == 0:
        return None

    params = {
        'timestamp': time.time()
    }

    bodys = {
        "versionIds": versionIds
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
    }
    res = requests.post(baseUrl + recommendModels, json=bodys, params=params, headers=headers)
    # logging.info(json.dumps(res.json(), ensure_ascii=False))
    return res.json()["data"]


# 获取模型直连地址
def get_direct_link(model_uuid):
    if model_uuid is None:
        return None
    if db.is_model_downloaded(model_uuid):
        logging.warning("模型已下载")
        return None
    model_info = get_model_info(model_uuid)
    if model_info:
        model_id = model_info["id"]
        # model_uuid = model_info["uuid"]
        model_name = model_info["name"]
        db.insert_model_info(model_uuid, model_name=model_name, model_info=json.dumps(model_info, ensure_ascii=False))
        model_type = model_info["modelType"]
        # 这里默认获取最新版本
        model_version_name = model_info["versions"][0]["name"]
        if model_info["versions"][0]["attachment"] is None:
            return None
        model_version_url = model_info["versions"][0]["attachment"]["modelSource"]
        model_version_desc = model_info["versions"][0]["versionDesc"]
        model_version_id = model_info["versions"][0]["id"]
        model_version_uuid = model_info["versions"][0]["uuid"]
        if model_info["versions"][0]["versionIntro"]:
            model_version_versionIntro = json.loads(model_info["versions"][0]["versionIntro"])
            if "ckpt" in model_version_versionIntro:
                base_model = model_version_versionIntro['ckpt']
                compatible_models = get_compatible_model(base_model)
                if compatible_models:
                    # logging.info("配套模型：")
                    for compatible_model in compatible_models:
                        # logging.info(
                        #     f'模型id ： {compatible_model["id"]}\r\n'
                        #     f'模型UUID ： {compatible_model["modelUuid"]}\r\n'
                        #     f'模型名称 ： {compatible_model["modelName"]}\r\n'
                        #     f'模型类型 ： {BaseModelType(compatible_model["baseType"]).desc()}\r\n'
                        #     f'模型版本名称 ：{compatible_model["modelVersionName"]}\r\n'
                        # )
                        get_direct_link(compatible_model['modelUuid'])

        check_download = get_check_download(model_id, model_name, model_version_uuid, model_version_url, model_uuid)
        if check_download:
            download_url = get_download_url(model_uuid, model_version_url)
            # logging.info(
            #     f'模型名称 ： {model_name}\r\n'
            #     f'模型类型 ： {ModelType(model_type).desc()}\r\n'
            #     f'模型下载地址 ：{download_url}\r\n'
            #     f'模型介绍 ：{model_version_desc}\r\n'
            #     f'推荐参数 ：{model_version_versionIntro}\r\n'
            # )
            if download_url:
                url_suffix = get_url_suffix(download_url)
                model_path = f"{model_file_parent_dir}{ModelType(model_type).file_path()}/{model_name}({model_version_name}){url_suffix}"
                logging.info(f'# {model_name}({model_version_name})  模型链接（https://www.liblib.art/modelinfo/{model_uuid}）')
                logging.info(f'!wget -c "{download_url}" -O "{model_path}"')
                if autoDownload:
                    download_model_start(download_url, model_path)
                    save_model_info(model_info)
                    download_model_cover(model_info)  # 新增调用
                # logging.info("================================================================")
            else:
                logging.warning(f"获取模型({model_name})下载地址失败，请检查当前账号是否有下载权限")
        else:
            logging.warning("下载校验失败")
    else:
        logging.warning("模型不存在")
    time.sleep(1)


# 下载文件
def download_model_start(download_url, model_path):
    logging.info(f"正在下载文件：{download_url} 至 {model_path}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # 判断文件是否已存在
    if os.path.exists(model_path):
        logging.warning(f"⚠️ 文件已存在，跳过下载: {model_path}")
        return

    download_cmd = [
        'wget', '-c',
        download_url,
        '-O',
        f"{model_path}"
    ]

    logging.info("正在执行下载命令：")
    logging.info(' '.join(download_cmd))

    try:
        result = subprocess.run(download_cmd, check=True)
        logging.info("✅ 下载完成")
    except subprocess.CalledProcessError as e:
        logging.warning(f"❌ 下载失败: {e}")


# 保存模型原始数据
def save_model_info(model_info):
    if model_info:
        model_name = model_info["name"]
        model_type = model_info["modelType"]
        # 这里默认获取最新版本
        model_version_name = model_info["versions"][0]["name"]
        info_file_json = f"{model_file_parent_dir}{ModelType(model_type).file_path()}/{model_name}({model_version_name}).json"
        # 判断文件是否已存在
        if os.path.exists(info_file_json):
            logging.warning(f"⚠️ 文件已存在，跳过下载: {info_file_json}")
            return
        # 将文本写入文件
        with open(info_file_json, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=4)
            logging.info(f"已保存模型信息至 {info_file_json}")


# 下载封面图片
def download_model_cover(model_info):
    if model_info:
        model_name = model_info["name"]
        model_type = model_info["modelType"]
        # 这里默认获取最新版本
        model_version_name = model_info["versions"][0]["name"]
        cover_url = model_info["versions"][0]["imageGroup"]["coverUrl"]
        img_suffix = get_url_suffix(cover_url)
        file_path = f"{model_file_parent_dir}{ModelType(model_type).file_path()}/{model_name}({model_version_name}){img_suffix}"
        # 判断文件是否已存在
        if os.path.exists(file_path):
            logging.warning(f"⚠️ 文件已存在，跳过下载: {file_path}")
            return
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 下载图片
        try:
            response = requests.get(cover_url, stream=True)
            response.raise_for_status()  # 检查请求状态
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            logging.info(f"✅ 封面图片已成功下载至: {file_path}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"❌ 下载封面图片失败: {e}")


# 初始化参数
def init():
    global TOKEN, CID, autoDownload, model_file_parent_dir
    setup_logging()  # 初始化日志系统
    logging.info("开始初始化程序...")
    # 获取 TOKEN
    config = file_util.read_yml()
    TOKEN = config.get('token')
    CID = config.get('cid')
    model_file_parent_dir = config.get('model_file_parent_dir')
    autoDownload = config.get('auto_download_models')

    if TOKEN:
        logging.info(f"成功读取 TOKEN : {TOKEN}")
    else:
        logging.warning("未找到 TOKEN，请检查 conf.yml 文件")


# 菜单
def menu():
    print("===============================")
    print("0. 返回菜单")
    print("1. 搜索自动模型")
    print("2. 通过链接下载模型")
    print("q. 退出")
    print("===============================")
    choice = input("请选择：")
    if choice == "0":
        menu()
    elif choice == "1":
        print("请输入关键字：")
        search_model_download_menu()
    elif choice == "2":
        download_model_menu()


def download_model_menu():
    # 接收输入
    print("请输入模型链接：")
    print(
        "样例：https://www.liblib.art/modelinfo/c4dbdde32eef41618b514b126aedb853?from=search&versionUuid=9248fef8f5074c3eb5f43d5f28838bef")
    while True:
        url = input("粘贴在这里（输入 q 退出程序，输入 0 返回菜单）：")
        if url == "0":
            menu()
            break
        if url == "q":
            exit()
            break
        if url == "":
            print("请输入模型链接：")
            continue
        model_uuid = get_model_id_by_url(url)
        if model_uuid is None:
            print("无法获取模型编号")
            continue
        get_direct_link(model_uuid)


def search_model_download_menu():
    # 接收输入
    print("请输入搜索关键字：")
    print("样例：情趣")
    while True:
        order = input("关键字（输入 q 退出程序，输入 0 返回菜单）：")
        if order == "0":
            menu()
            break
        if order == "q":
            exit()
            break
        if order == "":
            print("请输入搜索关键字：")
            continue
        uuids = search_model("情趣")
        for uuid in uuids:
            get_direct_link(uuid)

if __name__ == '__main__':
    init()
    menu()
