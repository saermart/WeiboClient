#!/usr/bin/python
# coding:utf-8


import time
from functools import wraps, partial

from utils.log import get_logger

log = get_logger(__name__)


def catch(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error(f'Function::{func.__name__}: {e}.')
    
    return inner


def web_cookie_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(args[0], 'web_cookie') and getattr(args[0], 'web_cookie'):
            return func(*args, **kwargs)
        else:
            raise Exception("No web web_cookie passed.")
    
    return inner


def mobile_cookie_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(args[0], 'mobile_cookie') and getattr(args[0], 'mobile_cookie'):
            return func(*args, **kwargs)
        else:
            raise Exception("No web mobile_cookie passed.")
    
    return inner


def cookie_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if hasattr(args[0], 'cookie') and getattr(args[0], 'cookie'):
            return func(*args, **kwargs)
        else:
            raise Exception("No cookie passed.")
    
    return inner


def add_func_result(func_name):
    '''
    只有两个函数的所有参数相同才可以使用此装饰器
    :param func_name: 添加返回数据的函数名
    :param is_private: 该函数是否为私有方法
    :return: 更新合并后的结果数据
    '''
    
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            added_data = {}
            name = func_name if not func_name.startswith('__') \
                else f"_{args[0].__class__.__name__}{func_name}"
            if hasattr(args[0], name):
                attr_func = getattr(args[0], name)
                if callable(attr_func):
                    added_data = attr_func(*args[1:], **kwargs)
            data = func(*args, **kwargs)
            if isinstance(data, dict) and isinstance(added_data, dict):
                data.update(added_data)
            return data
        
        return inner
    
    return wrapper


def retry(times=-1, delay=0, exceptions=Exception, logger=log):
    """
    inspired by https://github.com/invl/retry
    :param times: retry times
    :param delay: internals between each retry
    :param exceptions: exceptions may raise in retry
    :param logger: log for retry
    :return: func result or None
    """
    
    def _inter_retry(caller, retry_time, retry_delay, es):
        while retry_time:
            try:
                return caller()
            except es as e:
                retry_time -= 1
                if not retry_time:
                    logger.error("max tries for {} times, {} is raised, details: func name is {}, func args are {}".
                                 format(times, e, caller.func.__name__, (caller.args, caller.keywords)))
                    raise
                time.sleep(retry_delay)
    
    def retry_oper(func):
        @wraps(func)
        def _wraps(*args, **kwargs):
            return _inter_retry(partial(func, *args, **kwargs), times, delay, exceptions)
        
        return _wraps
    
    return retry_oper
