#!/usr/bin/python
# coding:utf-8

# MongoDB数据库设置
MONGO = {
    'host': 'localhost',
    'port': 27017,
    'database': '数据采集_微博_M版',  # 默认数据库
    'user': '',
    'password': '',
    'table': '',  # 默认集合名称
}

# 请求重试次数
REQUEST_RETRY_TIMES = 3
# SUB COOKIES请求重试次数与延迟请求间隔(秒)
COOKIE_RETRY_TIMES = 10
COOKIE_RETRY_DELAY = 1

# ***************** 日志设置 *****************
# 启用日志
LOG_ENABLE = True
# 日志级别
LOG_LEVEL = 'INFO'
# 日志文件编码
LOG_FILE_ENCODING = 'UTF-8'
# 日志文件路径
LOG_FILE_SAVE_PATH = r'logs/log.txt'
# 日志时间格式
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# 日志级别对应格式
LOG_FORMAT = {
    'DEBUG': '[%(lineno)d] %(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'INFO': '[%(lineno)d] %(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'WARNING': '[%(lineno)d] %(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'ERROR': '[%(lineno)d] %(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'CRITICAL': '[%(lineno)d] %(asctime)s %(name)s(%(levelname)s) - %(message)s',
}
