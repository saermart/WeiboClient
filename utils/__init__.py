#!/usr/bin/python
# coding:utf-8


import codecs
import hashlib
import random
import string
import time


def random_chars(length=6):
    return ''.join(
        [random.choice(
            string.ascii_lowercase + string.digits)
            for _ in range(length)
        ])


def read_data(file_path):
    with codecs.open(file_path, 'rb') as f:
        data = f.read()
        return data


def get_md5(bstr):
    m = hashlib.md5()
    m.update(bstr)
    return m.hexdigest()


def time_to_date(timestamp, format: str = "%Y-%m-%d %H:%M:%S"):
    timearr = time.localtime(timestamp)
    otherStyleTime = time.strftime(format, timearr)
    return otherStyleTime
