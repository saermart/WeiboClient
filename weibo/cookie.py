#!/usr/bin/python
# coding:utf-8


import json
import random
import re
from urllib import parse

import requests

from config import COOKIE_RETRY_TIMES, COOKIE_RETRY_DELAY
from utils.decorators import retry
from weibo.api import WEB_INCARNATE_URL, WEB_VISITOR_URL
from weibo.header import FakeChromeUA


class CookieMaker(object):
    __user_agent = FakeChromeUA.get_ua()
    __browser_type, __browser_version = __user_agent.split(' ')[-2].split('/')
    __browser_info = ''.join((__browser_type, ','.join(__browser_version.split('.'))))
    __headers = {
        'User-Agent': __user_agent,
        'Referer': WEB_INCARNATE_URL,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Host': 'passport.weibo.com',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    __extract_pattern = r'({.*})'
    
    @classmethod
    def __get_tid_and_c(cls, post_url):
        """
        get all args including tid、c and w
        :return: tuple(tid, c, w)
        """
        fp = '{' + \
             '"os":"1","browser":"{browser}","fonts":"undefined","screenInfo":"1436*752*24","plugins":"Portable ' \
             'Document Format::internal-pdf-viewer::Chrome PDF Plugin|::mhjfbmdgcfjbbpaeojofohoefgiehjai::Chrome PDF Viewer' \
             '|::internal-nacl-plugin::Native Client|Enables Widevine licenses for playback of HTML audio/video content. ' \
             '(version: 1.4.8.1008)::widevinecdmadapter.dll::Widevine Content Decryption Module"'.format(
                 browser=cls.__browser_info) \
             + '}'
        post_data = {
            'cb': 'gen_callback',
            'fp': fp
        }
        resp = requests.post(post_url, data=post_data, headers=cls.__headers)
        m = re.search(cls.__extract_pattern, resp.text)
        try:
            s = m.group()
            gen_visitor = json.loads(s)
            tid = gen_visitor.get('data').get('tid')
            c = gen_visitor.get('data').get('confidence', 100)
            if c != 100:
                c = '0' + str(c)
            new_tid = gen_visitor.get('data').get('new_tid')
        except AttributeError:
            raise Exception('failed to gen web_cookies without login')
        else:
            if str(new_tid).lower() == 'false':
                w = 2
            else:
                w = 3
            
            return tid, c, w
    
    @classmethod
    @retry(COOKIE_RETRY_TIMES, COOKIE_RETRY_DELAY)
    def get_cookies(cls):
        """
        :return: web_cookies: sub and subp
        """
        tid, c, w = cls.__get_tid_and_c(WEB_VISITOR_URL)
        r_tid = parse.quote_plus(tid)
        incarnate_url = WEB_INCARNATE_URL.format(r_tid, w, c, format(random.random(), '.17f'))
        cookies = {'tid': tid + '__' + c}
        resp = requests.get(incarnate_url, headers=cls.__headers, cookies=cookies)
        try:
            m = re.search(cls.__extract_pattern, resp.text)
            resp_str = m.group()
            if 'errline' in resp_str:
                raise Exception('Invalid web_cookie without login')
            s = json.loads(resp_str)
            sub = s.get('data').get('sub', '')
            subp = s.get('data').get('subp', '')
        except AttributeError:
            raise Exception('Failed to gen web_cookies without login')
        if not sub and not subp:
            raise Exception('Invalid web_cookie without login')
        return dict(SUB=sub, SUBP=subp)
