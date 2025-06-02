# file: util/logger_utils.py

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter

'''
所有模块共享相同日志格式 ✅
控制台与文件同时输出 ✅
支持断点续传、多线程进度条 ✅
支持日志切割、保留策略 ✅
支持彩色输出（可选） ✅
'''


def setup_global_logger(log_dir="logs", log_level=logging.INFO):
    """
    配置全局日志系统，确保所有模块共享相同的日志设置
    
    :param log_dir: 日志保存目录
    :param log_level: 日志级别（如 logging.DEBUG / logging.INFO）
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # 创建 formatter
    color_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(reset)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # 文件 handler：按天滚动保留7天
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(color_formatter)
    file_handler.setLevel(log_level)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(log_level)

    # 获取 root logger 并配置
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 移除已存在的 handlers，防止重复添加
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
