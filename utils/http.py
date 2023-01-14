#!/usr/bin/python
# coding:utf-8

# @FileName:    http.py
# @Time:        2022/12/2 21:52
# @Author:      bubu
# @Project:     数据采集脚本库

import requests
from functools import wraps
from config import REQUEST_RETRY_TIMES
from utils.log import get_logger

log = get_logger(__name__)


def do_request(api, method='GET', timeout=None, retry=REQUEST_RETRY_TIMES):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            payloads: dict = func(*args, **kwargs)
            params = payloads.get('params')
            kws = payloads.get('kwargs', {})
            as_text = payloads.get('as_text')
            data = payloads.get('data')
            file = payloads.get('file')
            json = payloads.get('json')
            headers = payloads.get('headers')
            callback = payloads.get('callback')
            url = payloads.get('url', api)
            ctimeout = kwargs.get('timeout', timeout)
            # TODO 添加代理IP的使用
            try:
                response = requests.request(method.upper(),
                                            url,
                                            params=params,
                                            data=data,
                                            json=json,
                                            files=file,
                                            headers=headers,
                                            timeout=ctimeout,
                                            **kws)
                if as_text:
                    data = response.text
                else:
                    data = response.json()
                    if callback and callable(callback):
                        data = callback(data)
                if response.status_code in [404, ]:
                    log.error(f'【重试值{retry}】请求路由失败:{response.status_code},返回：{response.text}')
                    if retry <= 0:
                        return
                    return do_request(api, method, timeout, retry - 1)(func)(*args, **kwargs)
            except Exception as e:
                log.error(f'【重试值{retry}】请求错误:{e}')
                if retry <= 0:
                    return
                return do_request(api, method, timeout, retry - 1)(func)(*args, **kwargs)
            return data
        
        return inner
    
    return wrapper
