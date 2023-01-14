#!/usr/bin/python
# coding:utf-8


import os.path
import random
import uuid
from threading import Thread

from requests import Request, Session

from database import save_into_mongo
from utils import read_data, get_md5
from utils.decorators import web_cookie_required, \
    add_func_result, mobile_cookie_required, catch
from utils.http import do_request
from utils.img import read_video_cover
from weibo.api import *
from weibo.cleaner import *
from weibo.consts import Types, Video, Visible, SuperTopics, VideoRanking
from weibo.cookie import CookieMaker
from weibo.header import FAKE_M_HEADERS
from weibo.header import FakeChromeUA
from weibo.util import get_cs, get_cookie_item, allot_video_chunks, load_from_yaml


class WeiBoClient(object):
    
    def __init__(self, web_cookie=None, mobile_cookie=None, headers=FAKE_M_HEADERS):
        self.web_cookie = web_cookie
        self.mobile_cookie = mobile_cookie
        self.headers = headers
        self._cn_emotions = None
        self._display_channels = None
        self._hot_tweet_groups = None
        self.cookie_pool = {}
    
    @classmethod
    @catch
    def load_from_file(cls, filename: str):
        '''
        从cookie配置文件（yaml格式）中加在cookies
        :param filename: 配置文件路径
        '''
        cookie_data = load_from_yaml(filename, 'r')
        web_cookies = cookie_data.get('cookies').get('web')
        h5_cookies = cookie_data.get('cookies').get('h5')
        return WeiBoClient(web_cookie=random.choice(web_cookies),
                           mobile_cookie=random.choice(h5_cookies))
    
    @property
    def cn_emotions(self) -> dict:
        if not self._cn_emotions:
            self._cn_emotions = self.fetch_emotions()
        return self._cn_emotions
    
    @property
    def display_channels(self) -> list:
        if not self._display_channels:
            self._display_channels = self.fetch_channels()
        return self._display_channels
    
    @property
    def hot_tweet_groups(self) -> dict:
        if not self._hot_tweet_groups:
            self._hot_tweet_groups = self.fetch_hot_tweet_groups()
        return self._hot_tweet_groups
    
    @property
    def sub_cookies(self) -> str:
        sub_cookie: dict = CookieMaker.get_cookies()
        return ';'.join([f'{k}={v}' for k, v in sub_cookie.items()])
    
    @property
    def web_xhr_headers(self) -> dict:
        return {
            'User-Agent': FakeChromeUA.get_ua(),
            'Cookie': self.web_cookie,
            'x-requested-with': 'XMLHttpRequest',
            'origin': 'https://weibo.com',
            'referer': 'https://weibo.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-xsrf-token': get_cookie_item('XSRF-TOKEN', self.web_cookie),
        }
    
    @save_into_mongo(collectionName='用户信息精简版', differ='uid')
    @user_info_extractor()
    @do_request(M_COMMON)
    def fetch_user_info(self, uid, **kwargs) -> dict:
        '''
        【无cookie版】采集用户简要信息,其中粉丝数据超过一定数值会按照类似“100万+”这种形式展现，
        需要具体数值的可以使用带SUB键值cookie的接口query_user_details【需cookie版-自生成】来尝试
        获取用户详细的信息。
        :param uid: 用户的微博id
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        return {
            "params": {
                "jumpfrom": "weibocom",
                "sudaref": "login.sina.com.cn",
                "type": "uid",
                "value": uid,
                "containerid": f"100505{uid}",
            },
            "headers": self.headers,
        }
    
    @user_info_extractor(MODE_WEB)
    @do_request(WEB_USER_INFO)
    def __query_user_details(self, uid, **kwargs) -> dict:
        '''
        【cookie版-自生成或登录版】采集用户精确信息.合并query_user_detail使用返回全面的用户信息
        :param uid: 用户的微博id
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'uid': uid,
            },
            'headers': {
                "User-Agent": FakeChromeUA.get_ua(),
                "Cookie": self.web_cookie or self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='用户信息详细版', differ='uid')
    @add_func_result('__query_user_details')
    @user_details_extractor
    @do_request(WEB_USER_DETAIL)
    def query_user_details(self, uid, **kwargs) -> dict:
        '''
        【cookie版-自生成或登录版】采集用户详细全面的信息。其中返回的ip_location字段只有在登录cookie被传入
        后才会被采集到。自生成版本的cookie请求返回的为location字段
        :param uid: 用户的微博id
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'uid': uid,
            },
            'headers': {
                "User-Agent": FakeChromeUA.get_ua(),
                "Cookie": self.web_cookie or self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='用户微博', differ="mid")
    @user_tweets_extractor()
    @do_request(M_COMMON)
    def fetch_user_tweets(self, uid, since_id=None, **kwargs) -> dict:
        '''
        【无cookie版】采集用户发布的微博,数量较少的可以全部采集，数量较多的（未测试具体数值）
        可能会发生采集不完全的情况，此情况下可以使用备用的query_user_tweets接口尝试,用户
        权限设置半年内可见或其他时间段则无法采集全部。
        :param uid: 用户的微博id
        :param since_id: 翻页参数，根据结果传递，起始为None
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                "jumpfrom": "weibocom",
                "sudaref": "login.sina.com.cn",
                "type": "uid",
                "value": uid,
                "containerid": f'107603{uid}',
                "since_id": since_id,
            },
            "headers": self.headers,
        }
    
    @save_into_mongo(collectionName='用户微博', differ="mid")
    @user_tweets_extractor()
    @do_request(M_COMMON)
    def query_user_tweets(self, uid, since_id=None, **kwargs) -> dict:
        '''
        【无cookie版】采集用户发布的微博,数量较少的可以全部采集，数量较多的（未测试具体数值）
        可能会发生采集不完全的情况,用户权限设置半年内可见或其他时间段则无法采集全部。
        此接口测试过几个博主采集：一般采集上限在2000条左右，个别情况下（16w条数）可以达到10w+，足以采集一般博主微博。
        :param uid: 用户的微博id
        :param since_id: 翻页参数，根据结果传递，起始为None
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'containerid': f'230413{uid}_-_WEIBO_SECOND_PROFILE_WEIBO',
                'page_type': '03',
                'since_id': since_id,
            },
            'headers': self.headers,
        }
    
    @save_into_mongo(collectionName='用户微博or文章_web版本', differ="mid")
    @user_tweets_extractor(MODE_WEB)
    @do_request(WEB_USER_BLOGS)
    @web_cookie_required
    def crawl_user_tweets(self, uid, since_id=None, feature=0, **kwargs) -> dict:
        '''
        提示1: 需严格控制采集间隔（一般大于3s），防止被封号或者中断数据传输
        提示2: 部分博主设置仅对粉丝展示全部微博内容，如果当前cookie账户非该博主粉丝，则无法采集全部微博，
        该情况下建议使用无cookie版的query_user_tweets接口
        【cookie版-登录后】网页版采集用户发布的微博或文章,数量较少的可以全部采集，数量较多的（未测试具体数值）
        可能会发生采集不完全的情况,用户权限设置半年内可见或其他时间段则无法采集全部。需将登录后的cookie
        传进WeiBoCrawler实例初始化后调用即可，如：
        >>> web_cookie = "SUB=xxxxx;SUBP=xxxxxx;"
        >>> client = WeiBoClient(web_cookie)
        >>> uid = "23333333"
        >>> blogs = client.crawl_user_tweets(uid,collectionName="xxx的微博")
        即可将采集的最新N条用户微博存进集合名为"xxx的微博"的MongoDB数据库中
        :param uid: 用户的微博id
        :param since_id: 翻页参数，根据结果传递，起始为None
        :param feature: 类别id,
            0       微博
            10      文章
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名
        :return: 接口结果，dict格式
        '''
        params = {
            'uid': uid,
            'page': '1',
            'feature': feature,
        }
        if since_id:
            params.update({
                'page': since_id.split('kp')[-1],
                'since_id': since_id,
            })
        return {
            'params': params,
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                "Cookie": self.web_cookie
            },
        }
    
    @save_into_mongo(collectionName='用户粉丝列表', differ=["uid", 'next'])
    @user_relations_extractor()
    @do_request(M_COMMON)
    def fetch_user_fans(self, uid, since_id=None, **kwargs) -> dict:
        '''
        【免cookie版】采集用户粉丝列表。
        :param uid: 用户的微博id
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'containerid': f'231051_-_fans_-_{uid}',
                'since_id': since_id,
            },
            'headers': self.headers,
        }
    
    @save_into_mongo(collectionName='用户关注列表', differ=["uid", 'next'])
    @user_relations_extractor(MODE_FRIENDS)
    @do_request(M_COMMON)
    def fetch_user_friends(self, uid, since_id=None, **kwargs) -> dict:
        '''
        【免cookie版】采集用户粉丝列表。
        :param uid: 用户的微博id
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'containerid': f'231051_-_followers_-_{uid}',
                'page': since_id,
            },
            'headers': self.headers,
        }
    
    @save_into_mongo(collectionName='微博详情_bid版本', differ='mid')
    @do_request(WEB_TWEET_DETAILS)
    def query_tweet_details_by_bid(self, bid, **kwargs) -> dict:
        '''
        查询微博详情并保存,bid从类似“https://weibo.com/2656274875/Mj5OPcYNO”这样的链接获取
        :param bid: 微博的bid，如：Mj5OPcYNO，一般由复制微博链接获得
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return:微博详情，dict格式
        '''
        return {
            'params': {
                'id': bid,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
            },
        }
    
    @save_into_mongo(collectionName='微博详情_mid版本', differ='mid')
    @tweet_details_parser
    @do_request('')
    def query_tweet_details_by_mid(self, mid, **kwargs) -> dict:
        '''
        【推荐】查询微博详情并保存,mid从类似“https://weibo.com/2281157913/4844109725173085”这样的链接获取
        :param mid: 微博的mid，如：4844109725173085，一般由复制微博链接获得
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return:微博详情，dict格式
        '''
        return {
            'as_text': True,
            'url': M_BLOG_DETAILS + str(mid),
            'headers': self.headers,
        }
    
    @save_into_mongo(collectionName='实时热搜榜', differ='timestamp')
    @hot_ranks_extractor
    @do_request(WEB_HOTS)
    def fetch_hot_ranking(self, **kwargs) -> dict:
        '''
        实时微博热搜榜，一般分钟更新，返回当前实时热搜前50条
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 实时热搜
        '''
        return {
            'headers': {
                'Cookie': self.web_cookie or self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='实时话题榜', differ='timestamp')
    @hot_topics_extractor
    @do_request(WEB_HOT_TOPICS)
    def fetch_hot_topics(self, page=1, **kwargs) -> dict:
        '''
        实时微博话题榜，一般分钟更新，返回当前实时热搜话题前58条
        :param page: 翻页参数，起始为1，递增+1
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 实时话题榜
        '''
        return {
            'params': {
                'sid': 'v_weibopro',
                'category': 'all',
                'page': page,
                'count': 10,
            },
            'headers': {
                'Cookie': self.web_cookie or self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='用户微博一级评论_web版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor()
    @do_request(WEB_TWEET_COMMENTS)
    def fetch_tweet_comments(self, mid, since_id=None, by_hot: bool = True, **kwargs) -> dict:
        '''
        网页版-获取某条微博的一级评论
        :param mid: 用户的微博mid
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param by_hot: 为True时按照热度排序（降序），为False时则按照时间排序（降序）
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'flow': [1, 0][by_hot],
                'is_reload': 1,
                'id': mid,
                'is_show_bulletin': 2,
                'is_mix': 0,
                'max_id': since_id,
                'count': 20,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
            }
        }
    
    @save_into_mongo(collectionName='用户微博一级评论_m版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor(MODE_M)
    @do_request(M_BLOG_COMMENTS)
    @mobile_cookie_required
    def query_tweet_comments(self, mid, since_id=None, **kwargs) -> dict:
        '''
        手机版-获取某条微博的一级评论,此接口没有评论的回复数等信息
        :param mid: 用户的微博mid
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        headers = self.headers.copy()
        headers.update({
            'Cookie': self.mobile_cookie,
            'mweibo-pwa': '1',
            'X-Requested-With': 'XMLHttpRequest',
        })
        params = {
            'id': mid,
            'mid': mid,
            'max_id_type': '0',
        }
        if since_id:
            params.update({
                'max_id': since_id,
            })
        return {
            'params': params,
            'headers': headers,
        }
    
    @save_into_mongo(collectionName='用户微博评论回复列表_web版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor()
    @do_request(WEB_TWEET_CHILD_COMMENTS)
    def fetch_child_comments(self, comment_id, since_id=None, **kwargs) -> dict:
        '''
        网页版-获取某条微博一级评论的回复评论列表
        :param comment_id: 微博的评论id
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'is_reload': 1,
                'id': comment_id,
                'is_show_bulletin': 2,
                'is_mix': 1,
                'fetch_level': 1,
                'max_id': since_id,
                'count': 20,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                # 'Cookie': cls.web_cookie,
                'x-requested-with': 'XMLHttpRequest',
            }
        }
    
    @save_into_mongo(collectionName='用户微博评论回复列表_m版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor()
    @do_request(M_BLOG_CHILD_COMMENTS)
    @mobile_cookie_required
    def query_child_comments(self, comment_id, since_id=None, **kwargs) -> dict:
        '''
        手机版-获取某条微博一级评论的回复评论列表
        :param comment_id: 微博的评论id
        :param since_id: 翻页参数，根据返回结果的next字段传入
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        headers = FAKE_M_HEADERS.copy()
        headers.update({
            'Cookie': self.mobile_cookie,
        })
        return {
            'params': {
                'cid': comment_id,
                'max_id': since_id,
                'max_id_type': 0,
            },
            'headers': headers
        }
    
    @save_into_mongo(collectionName='用户微博点赞列表_m版本', differ=['root_mid', 'user.id'])
    @tweet_comments_extractor(MODE_M, key_total='total_likes_count')
    @do_request(M_BLOG_LIKES)
    def query_tweet_likes(self, mid, since_id=None, **kwargs) -> dict:
        '''
        手机版 获取微博点赞用户列表，有cookie则可以获取最多到50页，无cookie可以获取最多前10页
        :param mid: 微博id
        :param since_id: 翻页参数，初始为0，下一页则递增+1即可
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'id': mid,
                'page': since_id,
            },
            'headers': {
                'Cookie': self.mobile_cookie
            },
        }
    
    @save_into_mongo(collectionName='用户微博点赞列表_web版本', differ=['root_mid', 'user.id'])
    @tweet_comments_extractor(key_total='total_likes_count')
    @do_request(WEB_TWEET_LIKES)
    def fetch_tweet_likes(self, mid, since_id=None, **kwargs) -> dict:
        '''
        网页版 获取微博点赞用户列表，可以获取最多到10页
        :param mid: 微博id
        :param since_id: 翻页参数，初始为0，下一页则递增+1即可
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'attitude_type': 0,
                'attitude_enable': 1,
                'page': since_id,
                'count': 10,
                'id': mid,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='用户微博转发列表_web版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor(key_total='total_repost_count')
    @do_request(WEB_TWEET_REPOSTS)
    def fetch_tweet_reposts(self, mid, since_id=None, **kwargs) -> dict:
        '''
        网页版 获取微博转发列表，可以获取最多全部转发
        :param mid: 微博id
        :param since_id: 翻页参数，初始为0，下一页则递增+1即可
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'id': mid,
                'page': since_id,
                'moduleID': 'feed',
                'count': 20,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
            }
        }
    
    @save_into_mongo(collectionName='用户微博转发列表_m版本', differ=['root_mid', 'mid'])
    @tweet_comments_extractor(MODE_M, key_total='total_repost_count')
    @do_request(M_BLOG_REPOSTS)
    @mobile_cookie_required
    def query_tweet_reposts(self, mid, since_id=None, **kwargs) -> dict:
        '''
        手机版【cookie版本】 获取微博转发列表，可以获取最多全部转发
        :param mid: 微博id
        :param since_id: 翻页参数，初始为0，下一页则递增+1即可
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        headers = FAKE_M_HEADERS.copy()
        headers.update({
            'Cookie': self.mobile_cookie,
        })
        return {
            'params': {
                'id': mid,
                'page': since_id,
            },
            'headers': headers
        }
    
    @save_into_mongo(collectionName='用户微博打赏列表_web版本', differ=['root_mid', 'timestamp'])
    @tweet_rewards_parser
    @do_request(WEB_TWEET_REWARDS)
    def fetch_tweet_rewards(self, mid, **kwargs) -> dict:
        '''
        获取某条微博的打赏用户列表，分为现金打赏和积分打赏
        :param mid: 微博id
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'oid': mid,
                'have_score': 1
            },
            'headers': FAKE_M_HEADERS
        }
    
    @save_into_mongo(collectionName='热门微博and榜单_web版本', differ=['mid', 'group_id'])
    @hot_tweets_extractor
    @do_request(WEB_HOT_TWEETS_FEED)
    def fetch_hot_tweets(self, since_id=0, group_id=None, containerid=None, **kwargs) -> dict:
        '''
        获取当前热门微博推荐【热门榜单】【热门微博】
        :param since_id: 翻页参数，起始为0，下一页根据返回的结果中的next传入
        :param group_id: 热门微博的频道种类，可以由hot_tweet_groups接口获得具体种类
        :param containerid: 热门微博的频道种类，可以由hot_tweet_groups接口获得具体种类
            【热门榜单】可见 weibo.consts.HotTweets类：
            小时榜:    **HotTweets.HOURS
            昨  日:    **HotTweets.YESTERDAY
            前  日:    **HotTweets.BEFORE_YESTERDAY
            周  榜:    **HotTweets.WEEKS
            男  榜:    **HotTweets.MAN
            女  榜:    **HotTweets.LADY
            例如获取当前热门榜单中的小时榜第一页并将数据保存在MongoDB数据库的“当前小时榜”集合中：
            >>> from weibo.consts import HotTweets
            >>> client = WeiBoClient()
            >>> hour_board = client.fetch_hot_tweets(**HotTweets.HOURS,collectionName='当前小时榜')
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        params = {
            'refresh': 2,
            'group_id': 102803 if not group_id else group_id,
            'containerid': 102803 if not containerid else containerid,
            'extparam': 'discover|new_feed',
            'max_id': since_id,
            'count': 10,
        }
        if since_id == 0:
            params.update({
                'refresh': 1,
                'since_id': 0,
            })
        return {
            'params': params,
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            }
        }
    
    @save_into_mongo(collectionName='视频榜单_web版本', differ=['update_date', 'cate_id', 'next'])
    @video_ranks_extractor
    @do_request(WEB_VIDEO_BOARD, 'POST')
    @web_cookie_required
    def fetch_video_ranking(self, cate_id=VideoRanking.ALL, cursor=None, **kwargs) -> dict:
        '''
        【网页cookie版本】获取视频榜单
        :param cate_id: 视频榜单类别,具体可见weibo.consts.VideoRanking
            全站: 4418213501411061            VideoRanking.ALL
            美食: 4418219809678881            VideoRanking.FOOD
            游戏: 4418219809678883            VideoRanking.GAME
            搞笑幽默: 4418219809678869        VideoRanking.FUNNY
            音乐: 4418219809678875            VideoRanking.MUSIC
            体育: 4418219809678887            VideoRanking.SPORTS
            动漫: 4418219809678867            VideoRanking.COMIC
            汽车: 4418219805484549            VideoRanking.CARS
            旅游: 4418219805484537            VideoRanking.TRAVEL
            舞蹈: 4418219805484551            VideoRanking.DANCE
            知识: 4418219809678865            VideoRanking.KNOWLEDGE
        :param cursor: 翻页参数，起始为None，根据返回的next传入实现翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        data = {
            "Component_Billboard_Billboardlist": {
                "cid": f"{cate_id}",
                "count": 20
            }
        }
        params = {
            'page': '/tv/billboard'
        }
        if cursor:
            data['Component_Billboard_Billboardlist'].update({
                "next_cursor": cursor,
            })
        if cate_id is not VideoRanking.ALL:
            params = {
                'page': f'/tv/billboard/{cate_id}',
            }
        return {
            'data': {
                'data': json.dumps(data),
            },
            'params': params,
            'headers': self.web_xhr_headers,
        }
    
    @save_into_mongo(collectionName='视频号推荐_web版本', differ='timestamp')
    @video_stars_extractor
    @do_request(WEB_VIDEO_BOARD, 'POST')
    @web_cookie_required
    def fetch_video_star_feed(self, **kwargs) -> dict:
        '''
        获取热门视频号推荐 以及 优质视频号推荐
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'page': '/tv/star',
            },
            'data': {
                'data': json.dumps({"Component_Star_List": {}}),
            },
            'headers': self.web_xhr_headers,
        }
    
    @save_into_mongo(collectionName='视频推荐_web版本', differ='mid')
    @video_feed_extractor()
    @do_request(WEB_VIDEO_BOARD, 'POST')
    @web_cookie_required
    def fetch_video_feed(self, cursor=None, **kwargs) -> dict:
        '''
        获取网页版微博视频推荐流
        :keyword cursor: 翻页参数，起始为None，根据结果返回的next传入进行翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'page': '/tv/home',
            },
            'data': {
                'data': json.dumps(
                    {"Component_Home_Recommend": {"next_cursor": cursor}}
                ),
            },
            'headers': self.web_xhr_headers,
        }
    
    @save_into_mongo(collectionName='精选频道视频推荐_web版本', differ='mid')
    @video_feed_extractor('Component_Channel_Hot')
    @do_request(WEB_VIDEO_BOARD, 'POST')
    @web_cookie_required
    def fetch_channel_video_feed(self, channel_id, cursor=None, **kwargs) -> dict:
        '''
        【网页cookie版本】获取某个频道的推荐视频
        :param channel_id: 频道id，可以通过fetch_video_channels接口获取
        :param cursor: 翻页参数，起始为None，根据结果返回的next传入翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        params = {
            'page': f'/tv/channel/{channel_id}',
        }
        data = {
            "Component_Channel_Hot": {
                "next_cursor": cursor,
                "cid": channel_id,
            }
        }
        return {
            'params': params,
            'data': {
                'data': json.dumps(data),
            },
            'headers': self.web_xhr_headers,
        }
    
    @video_channels_extractor
    @do_request(WEB_VIDEO_BOARD, 'POST')
    def fetch_video_channels(self) -> dict:
        '''
        获取视频频道的具体信息
        :return:
        '''
        return {
            'params': {
                'page': f'/tv/home/',
                'm': 'home',
            },
            'data': {
                'data': json.dumps(
                    {"Component_Channel_Menu": {}}
                )
            },
            'headers': self.web_xhr_headers,
        }
    
    @hot_tweet_groups_extractor
    @do_request(WEB_HOT_GROUPS)
    def fetch_hot_tweet_groups(self) -> dict:
        '''
        获取热门微博频道种类
        :return:
        '''
        return {
            'params': {
                'is_new_segment': 1,
                'fetch_hot': 1,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
            }
        }
    
    @cn_emotions_extractor
    @do_request(WEB_EMOTICONS)
    def fetch_emotions(self) -> dict:
        '''
        获取微博默认表情包
        :return:
        '''
        return {
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': self.sub_cookies,
            },
        }
    
    @display_channels_extractor
    @do_request(WEB_DISPLAY_CHANNELS)
    def fetch_channels(self) -> dict:
        '''
        【网页cookie版本】获取当前可以发布微博的频道
        :return: 频道集合
        '''
        return {
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': self.sub_cookies,
            },
        }
    
    @do_request(WEB_USER_COLLECTIONS)
    @web_cookie_required
    def fetch_user_collections(self, page=1) -> dict:
        '''
        【网页cookie版本】获取当前cookie用户创建的所有视频合集
        :param page: 翻页参数，起始为1，递增+1
        :return: 合集
        '''
        return {
            'params': {
                'page': page,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': self.web_cookie,
            },
        }
    
    @user_groups_extractor
    @do_request(WEB_USER_GROUPS)
    @web_cookie_required
    def fetch_user_groups(self) -> dict:
        '''
        【网页cookie版本】获取当前cookie用户加入的所有群组
        :return:群组集合
        '''
        return {
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': self.web_cookie,
            },
        }
    
    @super_topics_extractor
    @do_request(WEB_USER_STOPICS)
    def fetch_super_topics(self, cate_id=SuperTopics.RECENTLY, page=1) -> dict:
        '''
        【网页cookie版本】获取超话集合信息
        :param cate_id: 超话类别id
            最近使用：   123333      SuperTopics.RECENTLY   [默认]
            本   地：    149         SuperTopics.LOCAL
            美好生活：   182         SuperTopics.LIVES
            闲   趣：    148         SuperTopics.INTERESTS
            明   星：    2           SuperTopics.STARS
            红   人：    184         SuperTopics.FAMOUS
            影视综艺：   181         SuperTopics.ADVERTISE
            体育运动：   98          SuperTopics.SPORTS
            游   戏：    126         SuperTopics.GAME
            电   竞：    187         SuperTopics.ESPORTS
            动   漫：    97          SuperTopics.COMICS
            读   书：    94          SuperTopics.READING
            好好学习：   133         SuperTopics.LEARNING
            校   园：    152         SuperTopics.CAMPUS
            企   业：    183         SuperTopics.ENTERPRISE
            公   益：    6           SuperTopics.WELFARE
            其   他：    8           SuperTopics.OTHERS
        :param page: 翻页参数，起始为1，递增+1
        :return: 超话详细
        '''
        return {
            'params': {
                'sort_id': cate_id,
                'page': page,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': self.sub_cookies,
            },
        }
    
    @do_request(M_COMMON)
    def search(self, keywords, category=Types.GENERAL, since_id=None, **kwargs) -> dict:
        '''
        关键词搜索微博【手机版】不需cookie最多可以搜索70页左右,加了cookie最多搜索200页左右
        由于分类搜索结果各不相同，所以此处没有做装饰器和数据库保存，有需要可以自己编写后加装饰器
        :param keywords: 关键词
        :param since_id: 翻页参数，初始为0，下一页则递增+1即可
        :param category: 需要搜索的分类,int型数值,可以导入weibo.consts的Types类
            1   - 综合    Types.GENERAL
            61  - 实时    Types.REALTIME
            3   - 用户    Types.USERS
            62  - 关注    Types.CONCERNS
            64  - 视频    Types.VIDEOS
            63  - 图片    Types.PICS
            21  - 文章    Types.ARTICLES
            60  - 热门    Types.HOTS
            38  - 话题    Types.TOPICS
            98  - 超话    Types.SUPERS
            92  - 地点    Types.LOCATIONS
            97  - 商品    Types.GOODS
            32  - 主页    Types.PAGES
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        headers = FAKE_M_HEADERS.copy()
        headers.update({
            'Cookie': self.mobile_cookie
        })
        return {
            'params': {
                'containerid': f'100103type={category}&q={keywords}&t=',
                'page_type': 'searchall',
                'page': since_id,
            },
            'headers': headers,
        }
    
    @save_into_mongo(collectionName='微博图片搜索_web版本', differ=['mid', 'keywords'])
    @pic_tweet_extractor
    @do_request(WEB_SEARCH_PICS)
    def search_pic(self, keywords, since_id=None, **kwargs) -> dict:
        '''
        网页版，关键词搜索图片微博
        :param keywords:搜索关键词
        :param since_id:翻页参数，初始为0，下一页则递增+1即可
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，dict格式
        '''
        return {
            'params': {
                'q': keywords,
                'page': since_id,
                '_t': 0,
                '__rnd': int(time.time() * 1000),
            },
            'headers': {
                'X-Requested-With': 'XMLHttpRequest',
                'referer': 'https://s.weibo.com/pic',
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            }
        }
    
    @stopics_extractor
    @do_request(WEB_USER_STOPICS)
    def search_super_topics(self, keyword, page=1) -> dict:
        '''
        关键词搜索超话，只有第一页
        :param keyword: 关键词
        :param page: 翻页参数，只有第一页有效
        :return: 结果
        '''
        return {
            'params': {
                'sort_id': 0,
                'keyword': keyword,
                'page': page,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            }
        }
    
    @web_cookie_required
    def __upload_video_init(self, video_data, video_name) -> dict:
        '''
        【网页cookie版本】上传视频前的初始化工作，获取视频上传的upload_id和media_id以及视频分块大小和上传协议
        :param video_data: 视频数据
        :param video_name: 视频名称
        :return:初始化结果
        '''
        req = Request('POST',
                      WEB_UPLOAD_INIT,
                      headers=self.web_xhr_headers,
                      params={
                          'ab': '8143-g0%2C7598-g0',
                          'source': '339644097',
                          'size': len(video_data),
                          'name': video_name,
                          'type': 'video',
                          'client': 'web',
                      },
                      files={
                          'biz_file': (None, b'{"mediaprops":"{\'screenshot\':1}"}')
                      })
        s = Session()
        prepped = s.prepare_request(req)
        prepped.headers['Content-Type'] = 'multipart/mixed; boundary=' + \
                                          prepped.body.split(b"\r\n")[-2][2:-2].decode()
        resp = s.send(prepped)
        data = resp.json()
        return data
    
    @do_request(WEB_UPLOAD_VIDEO, 'POST')
    @web_cookie_required
    def __upload_video(self, params, video_data) -> dict:
        '''
        【网页cookie版本】 上传视频数据
        :param params: 参数
        :param video_data: 视频字节流
        :return: 上传结果
        '''
        headers = self.web_xhr_headers.copy()
        headers.update({
            'Content-Type': 'application/octet-stream',
            'Host': 'up.video.weibocdn.com',
        })
        return {
            'params': params,
            'data': video_data,
            'headers': headers,
            'callback': lambda x: log.info(f'【上传视频】上传视频分块成功:{x}') or x
        }
    
    @do_request(WEB_CHECK_UPLOAD, 'POST')
    @web_cookie_required
    def __check_upload_video_status(self, payload) -> dict:
        '''
        【网页cookie版本】查询视频上传的结果，结果中result字段为true则表明成功
        :param payload:查询参数，dict类型
        :return:查询结果，例如：
        {
            "result":true,
            "upload_id":"8EE2E051221C4E55AE6E7A740DE3DB17",
            "media_id":"4847078531334225",
            "auth":"xxxxxx",
            "request_id":"req_2c4b8e7e104ee6ba"
        }
        '''
        return {
            'data': payload,
            'headers': self.web_xhr_headers
        }
    
    @web_cookie_required
    def upload_video(self,
                     video_path_or_data,
                     video_name=None,
                     up_threads=2,
                     watermark='@saermart'):
        '''
        【网页cookie版本】发布视频微博前必须先上传视频。可以是本地视频或者网络视频数据流
        如果是本地视频上传，会自动截图第一帧图片上传，也可以使用自定义图片作为封面发微博
        :param video_path_or_data:本地视频绝对路径或者网络视频字节数据流
        :param video_name:视频名称，默认按照本地存储名为准，视频流则默认用uuid+时间戳命名
        :param up_threads:上传视频线程数
        :param watermark:上传视频封面的水印文字
        :return:视频上传结果
        '''
        if isinstance(video_path_or_data, bytes):
            video_data = video_path_or_data
            video_name = video_name if video_name else f'{uuid.uuid4()}-{int(time.time() * 1000)}.mp4'
        elif not os.path.isfile(video_path_or_data):
            raise Exception(f'【上传视频】无法找到视频文件.{video_path_or_data}')
        else:
            video_name = video_name if video_name else os.path.basename(video_path_or_data)
            video_data = read_data(video_path_or_data)
        # 视频上传前的初始化设置，获得upload_id和视频的media_id以及上传分块大小
        try:
            upload_inited = self.__upload_video_init(video_data, video_name)
            if upload_inited.get('error'):
                msg = upload_inited.get('error').get('msg')
                raise Exception(f'请检查cookie有效性！原因：{msg}')
        except Exception as e:
            log.error(f'【上传视频】上传视频初始化失败:{e}')
            return
        else:
            upload_id = upload_inited.get('upload_id')
            media_id = upload_inited.get('media_id')
            strategy = upload_inited.get('strategy', {})
            upload_protocol = strategy.get('upload_protocol', 'binary')
            chunk_size = strategy.get('chunk_size', 8192)
            log.info(f'【上传视频】视频上传初始化成功.预计视频id:{media_id}')
            # 对需要上传的视频进行分块上传
            video_chunks = allot_video_chunks(video_data, chunk_size)
            count = len(video_chunks)
            while video_chunks:
                threads = []
                for i in range(min(up_threads, len(video_chunks))):
                    if not video_chunks:
                        break
                    chunk = video_chunks.pop(0)
                    params = {
                        'source': '339644097',
                        'upload_id': upload_id,
                        'media_id': media_id,
                        'upload_protocol': upload_protocol,
                        'type': 'video',
                        'client': 'web',
                        'check': get_md5(chunk.get('data')),
                        'index': chunk.get('index'),
                        'size': chunk.get('size'),
                        'start_loc': chunk.get('start'),
                        'count': count,
                    }
                    threads.append(Thread(target=self.__upload_video, args=(params, chunk.get('data'))))
                for i in threads:
                    i.start()
                for i in threads:
                    i.join()
            log.info(f'【上传视频】视频分块上传步骤通过: {count} 块共 {len(video_data)} 字节 ')
            log.info(f'【上传视频】开始查询上传结果...')
            status = self.__check_upload_video_status({
                'source': '339644097',
                'upload_id': upload_id,
                'media_id': media_id,
                'upload_protocol': upload_protocol,
                'action': 'finish',
                'client': 'web',
                'size': len(video_data),
                'count': count,
                'status': None,
            })
            if status and status.get('result'):
                mid = status.get("media_id")
                log.info(f'【上传视频】查询结果：上传视频成功！视频id: {mid}')
                # 获取本地视频封面截图并上传,自动截图第一帧
                if os.path.isfile(video_path_or_data):
                    cover = read_video_cover(video_path_or_data)
                    pic_res = self.upload_picture(cover, watermark)
                    if pic_res.get('ret'):
                        pid = pic_res.get('pic').get('pid')
                        status.update({
                            'cover_pid': pid,
                        })
                        log.info(f'【上传视频】【封面备选】上传视频截图成功.pid:{pid}')
                return status
    
    @do_request(WEB_UPLOAD_PIC, 'POST')
    @web_cookie_required
    def upload_picture(self, pic_path_or_data, watermark='@saermart') -> dict:
        '''
        【网页cookie版本】上传图片至微博，返回图片上传后的pid用于微博发布等使用
        :param pic_path_or_data: 图片的本地路径或者图片的二进制数据
        :param watermark: 需要加在图片上的水印文字,如：@某个微博用户昵称
        :return: 接口结果
        '''
        if os.path.isfile(pic_path_or_data):
            pic = read_data(pic_path_or_data)
        else:
            pic = pic_path_or_data
        md5 = get_md5(pic)
        return {
            'params': {
                'file_source': 1,
                'ent': 'miniblog',
                'appid': '339644097',
                'raw_md5': md5,
                'ori': '1',
                'cs': get_cs(pic),
                'mpos': '1',
                'uid': '',
                'nick': watermark,
            },
            'data': pic,
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.web_cookie,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'picupload.weibo.com',
            }
        }
    
    @do_request(WEB_FOLLOW_STOPICS)
    @web_cookie_required
    def follow_super_topic(self, topic_id, name, is_obturate=0) -> dict:
        '''
        【网页cookie版本】关注超话
        :param topic_id: 超话id，可以由接口fetch_super_topics获取超话信息
        :param name: 超话名称
        :param is_obturate:
        :return: 关注结果
        '''
        return {
            'params': {
                'oid': topic_id,
                'display_name': name,
                'is_obturate': is_obturate,
            },
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_UPDATE_TWEET, 'POST')
    @web_cookie_required
    def post_tweet(self,
                   content,
                   pid=None,
                   mid=None,
                   video_title="",
                   video_type=Video.ORIGINAL,
                   collection_ids="",
                   video_down=False,
                   channel_ids="",
                   schedule=None,
                   visible=Visible.PUBLIC,
                   share_id=None,
                   topic_id=None,
                   topic_name=None,
                   sync=True,
                   ) -> dict:
        '''
        【网页cookie版本】发布微博,可以带图片也可以是视频微博,发布视频微博需要先上传视频和视频封面，
        发布图片微博也需要先上传图片，再添加其他的文字等.
        :param content: 微博文字内容，可以用英文中括号[]加表情，如:[杰克·萨利]加油~@saermart #崩溃了# #北京[地点]#
        :keyword pid:
            1. 图片微博则为图片的pid，多图片则用英文逗号隔开pid,如：008syIOLly1xxx,008syIOLlyxxx
            2. 视频微博则为已上传的视频封面图片的pid
            3. 纯文字微博则无需填写
        :keyword mid: 传值则表示发布的为视频微博，表示的是已经上传的视频的media_id, pid则变为必填。已发布的mid不适合继续发布.
        :keyword video_title: 视频的标题, str型
        :keyword video_type: 视频类型，int型:
              原创: 0   ==  Video.ORIGINAL
              二创: 2   ==  Video.SECOND
              转载: 1   ==  Video.REPOST
              版权: 3   ==  Video.COPYRIGHT
        :keyword collection_ids: 视频合集id，str型，可以通过fetch_user_collections接口获取
        :keyword video_down: 是否可以下载该视频, bool型
        :keyword channel_ids: 发布视频微博的所在频道, str型，可以通过display_channels接口获取
        :keyword schedule: 发布定时微博的时间戳,13位,例如：1671267720825
        :keyword visible: 微博可见对象:
            公开:          0      Visible.PUBLIC
            粉丝:          10     Visible.FANS
            好友圈:        10     Visible.FRIENDS
            仅自己可见:    10     Visible.SELF
            群可见:        5      Visible.GROUPS
            当为群可见的时候，share_id为必填项，可以从fetch_user_groups接口获取群的page_objectid传入
        :keyword topic_id: 发布超话的topic_id，未关注的超话则需要先通过接口follow_super_topic关注后才能发布对于超话下的微博，
        可以从fetch_super_topics接口获取,需要注意的是，超话微博必须是公开的
        :keyword topic_name:超话名称
        :keyword sync: 发布超话是否同步发布到微博,bool型，默认同步
        :return: 微博发布结果
        '''
        if mid and not pid:
            raise Exception('缺少视频封面的pid.')
        if schedule and int(schedule) - int(time.time() * 1000) < 60 * 10 * 1000:
            raise Exception(f'定时公布微博时间必须至少在10分钟后.')
        media_info = {
            "titles": [{"title": video_title, "default": "true"}],
            "covers": [{"pid": pid}],
            "type": "video",
            "media_id": mid,
            "resource": {"video_down": [0, 1][video_down]},
            "homemade": {"channel_ids": [channel_ids], "type": video_type},
            "approval_reprint": "1",
        } if mid else {}
        if collection_ids and mid:
            media_info.update({
                "playlist": {"playlist_video": True, "album_ids": collection_ids}
            })
        data = {
            'content': content,
            'pic_id': pid if not mid else '',
            'visible': visible,
            'share_id': share_id,
            'media': f'{json.dumps(media_info)}',
            'vote': '{}',
            'approval_state': '0',
        }
        if topic_id and topic_name:
            if visible is not Visible.PUBLIC:
                raise Exception('超话微博必须为公开的.')
            data.update({
                'content': f'#{topic_name}[超话]# {content}',
                'topic_id': topic_id,
                'sync_mblog': [0, 1][sync]
            })
        if schedule:
            data.update({
                'schedule_timestamp': schedule,
                'schedule_id': None,
            })
        # 如果非公开则分情况传参
        if visible:
            if visible is Visible.GROUPS:
                if not share_id:
                    raise Exception('缺少可见群share_id')
                else:
                    data.update({
                        'share_id': share_id,
                    })
            else:
                data.pop('share_id')
        ret = {
            'data': data,
            'headers': self.web_xhr_headers,
        }
        if schedule:
            ret.update({
                'url': WEB_SCHEDULE_POST,
            })
        return ret
    
    @do_request(WEB_DELETE_TWEET, 'POST')
    @web_cookie_required
    def delete_tweet(self, mid) -> dict:
        '''
        【网页cookie版本】删除当前用户的微博
        :param mid: 微博id
        :return: 删除结果
        '''
        return {
            'data': {
                'id': mid
            },
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_QUICK_REPOST, 'POST')
    @web_cookie_required
    def quick_repost_tweet(self, mid) -> dict:
        '''
        【网页cookie版本】快转微博
        :param mid: 需要快转的微博id
        :return:
        '''
        return {
            'data': {
                "id": mid,
                "is_comment": 0,
                "is_fast": 1
            },
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_REPOST, 'POST')
    @web_cookie_required
    def repost_tweet(self,
                     mid,
                     cid=None,
                     content='转发微博',
                     pid=None,
                     share_id=None,
                     comment=False,
                     visible=Visible.PUBLIC,
                     ) -> dict:
        '''
        【网页cookie版本】转发微博，可以转发微博下的评论，也可以转发的同时评论
        :param mid: 要转发的微博id
        :param cid: 要转发的微博评论的id,转发评论时要将评论内容传入content，不然无法自动获得要转发的评论内容
        :param content: 转发时写的内容
        :param pid: 转发时加入的图片pid，需要先上传图片获得pid
        :param share_id: 转发群可见时需要加入群id，可以从fetch_user_groups接口获得
        :param comment: 是否转发的同时评论，默认不评论为False
        :param visible: 可见性，一般是公开，可见Visible下的属性
        :return:转发结果
        '''
        if visible is Visible.GROUPS and not share_id:
            raise Exception('可见性为群可见时必须传入share_id.')
        data = {
            'id': mid,
            'comment': content,
            'pic_id': pid,
            'is_repost': 0,
            'comment_ori': 0,
            'is_comment': [0, 1][comment],
            'visible': visible,
            'share_id': share_id,
        }
        if cid:
            data.update({
                'cid': cid,
            })
        return {
            'data': data,
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_COMMENT_TWEET, 'POST')
    @web_cookie_required
    def comment_tweet(self, mid, content, pid=None, repost=False, **kwargs) -> dict:
        '''
        【网页cookie版本】对微博进行评论,可以评论同时转发
        :param mid: 需要评论的微博id
        :param content: 评论内容
        :param pid: 要添加进评论的图片pid，需要先上传图片，当前网页版微博不允许评论带图片，可以转发带图片评论
        :param repost: 是否评论的同时转发
        :param kwargs: 其他
        :return: 评论结果
        '''
        return {
            'data': {
                'id': mid,
                'comment': content,
                'pic_id': pid,
                'is_repost': [0, 1][repost],
                'comment_ori': 0,
                'is_comment': 0,
            },
            'headers': self.web_xhr_headers
        }
    
    @do_request(WEB_COMMENT_REPLY, 'POST')
    @web_cookie_required
    def reply_to_comment(self, mid, cid, content, repost=False, pid=None, **kwargs) -> dict:
        '''
        【网页cookie版本】对微博评论进行回复，可以回复同时转发评论和微博
        :param mid: 微博id
        :param cid: 要回复的评论id
        :param content: 回复内容
        :param repost:是否回复同时转发
        :param pid: 需要添加进回复内容的图片id，需要先上传图片，默认无法图片评论
        :param kwargs: 其他
        :return: 回复结果
        '''
        return {
            'data': {
                'id': mid,
                'cid': cid,
                'comment': content,
                'pic_id': pid,
                'is_repost': [0, 1][repost],
                'comment_ori': 0,
                'is_comment': 0,
            },
            'headers': self.web_xhr_headers
        }
    
    @do_request(WEB_COMMENT_DELETE, 'POST')
    @web_cookie_required
    def delete_comment(self, cid) -> dict:
        '''
        【网页cookie版本】 对当前用户的评论进行删除
        :param cid: 评论id
        :return:
        '''
        return {
            'data': {
                "cid": cid,
                "filter": {}
            },
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_FOLLOW_USER, 'POST')
    def follow_user(self, uid) -> dict:
        '''
        【网页cookie版本】关注用户
        :param uid: 用户uid
        :return: 用户信息
        '''
        return {
            'data': {"friend_uid": uid},
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_UNFOLLOW_USER, 'POST')
    def unfollow_user(self, uid) -> dict:
        '''
        【网页cookie版本】取消关注用户
        :param uid: 用户uid
        :return: 用户信息
        '''
        return {
            'data': {"uid": uid},
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_LIKE_TWEET, 'POST')
    def like_tweet(self, mid) -> dict:
        '''
        【网页cookie版本】点赞微博
        :param mid: 微博id
        :return: 微博信息
        '''
        return {
            'data': {"id": mid},
            'headers': self.web_xhr_headers,
        }
    
    @do_request(WEB_UNLIKE_TWEET, 'POST')
    def unlike_tweet(self, mid) -> dict:
        '''
        【网页cookie版本】取消点赞微博
        :param mid: 微博id
        :return: 取消结果
        '''
        return {
            'data': {"id": mid},
            'headers': self.web_xhr_headers,
        }
    
    @save_into_mongo(collectionName='关注朋友的微博_web版本', differ='mid')
    @user_friends_tweets
    @do_request(WEB_FRIENDS_TWEETS)
    @web_cookie_required
    def fetch_my_friends_tweets(self, since_id=0, **kwargs) -> dict:
        '''
        【网页cookie版本】 获取当前cookie用户的关注的朋友新发布的微博
        :param since_id: 翻页参数，起始为0，根据返回的next传入进行翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，list格式
        '''
        params = {
            'refresh': 4,
            'since_id': since_id,
            'count': 15,
        }
        if since_id:
            params.update({
                'max_id': since_id,
            })
            params.pop('since_id')
        return {
            'params': params,
            'headers': self.web_xhr_headers
        }
    
    @save_into_mongo(collectionName='博主精选微博_web版本', differ=['mid', 'user.uid'])
    @user_hots_extractor()
    @do_request(WEB_USER_HOTS)
    def fetch_user_hots(self, uid, page=1, **kwargs) -> dict:
        '''
        获取某个用户的精选微博列表
        :param uid: 用户id
        :param page:翻页参数，起始为1，默认递增+1进行翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，list格式
        '''
        return {
            'params': {
                'page': page,
                'feature': 2,
                'uid': uid,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            },
        }
    
    @save_into_mongo(collectionName='博主视频_web版本', differ=['mid', 'user.uid'])
    @user_hots_extractor()
    @do_request(WEB_USER_VIDEOS)
    def fetch_user_videos(self, uid, cursor=0, **kwargs) -> dict:
        '''
        获取某个用户的视频列表
        :param uid: 用户id
        :param cursor:翻页参数，起始为0，根据返回结果中的next传入进行翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，list格式
        '''
        return {
            'params': {
                'cursor': cursor,
                'uid': uid,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            },
        }
    
    @save_into_mongo(collectionName='博主微博图片_web版本', differ=['mid', 'pid'])
    @user_hots_extractor('since_id')
    @do_request(WEB_USER_PICS)
    def fetch_user_pictures(self, uid, cursor=0, has_album=False, **kwargs) -> dict:
        '''
        获取某个用户的图片列表
        :param uid: 用户id
        :param cursor:翻页参数，起始为0，根据返回结果中的next传入进行翻页
        :param has_album: 是否有相册
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，list格式
        '''
        return {
            'params': {
                'sinceid': cursor,
                'uid': uid,
                'has_album': has_album,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            },
        }
    
    @save_into_mongo(collectionName='博主微博相册图片_web版本', differ=['mid', 'pid'])
    @user_hots_extractor('since_id')
    @do_request(WEB_USER_ALBUM_PICS)
    def fetch_user_album_pictures(self, container_id, cursor=0, **kwargs) -> dict:
        '''
        获取某个用户的图片列表
        :param container_id: 相册id,可以由fetch_user_albums接口获取
        :param cursor:翻页参数，起始为0，根据返回结果中的next传入进行翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return: 接口结果，list格式
        '''
        return {
            'params': {
                'since_id': cursor,
                'containerid': container_id,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            },
        }
    
    @user_albums_extractor
    @do_request(WEB_USER_PICS)
    def fetch_user_albums(self, uid) -> dict:
        '''
        获取博主微博相册
        :param uid: 博主uid
        :return:相册信息
        '''
        return {
            'params': {
                'sinceid': 0,
                'uid': uid,
                'has_album': True,
            },
            'headers': {
                'User-Agent': FakeChromeUA.get_ua(),
                'Cookie': self.sub_cookies,
            },
        }
    
    @do_request(WEB_USER_COMMENTS)
    @web_cookie_required
    def fetch_my_comments(self, cursor=None, **kwargs):
        '''
        【网页cookie版】获取当前cookie用户发出过的评论
        :param cursor: 翻页参数，起始为None，根据返回结果next、previous传入进行上下翻页
        :param kwargs: 可选关键字参数如下
            :keyword db_instance: MongoDB数据库实例，默认内置配置的实例
            :keyword into_mongo: bool值，保存结果至mongodb数据库,默认不保存,collectionName填写则默认启动保存
            :keyword dbName: 保存至MongoDB数据库的数据库名
            :keyword collectionName: 保存至MongoDB数据库的集合名
            :keyword differ: 查询是否已采集保存至数据库的最外层键名,多个条件则可以是list
        :return:
        '''
        return {
            'params': {
                'max_id': f'{cursor}',
            },
            'headers': self.web_xhr_headers,
        }
