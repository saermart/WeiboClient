#!/usr/bin/python
# coding:utf-8

import json
import time
from functools import wraps

import w3lib.url

from utils import time_to_date
from utils.log import get_logger
from weibo.api import MODE_M, MODE_WEB, MODE_FANS

log = get_logger(__name__)


def user_relations_extractor(mode=MODE_FANS):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response: dict = func(*args, **kwargs)
            data: dict = response.get('data')
            cards: list = data.get('cards')
            cardlistInfo: dict = data.get('cardlistInfo')
            total = cardlistInfo.get('total')
            page = cardlistInfo.get('page')
            uid = None
            users = []
            info = []
            ret = {
                'uid': uid,
                'total': total,
                'next': page,
                'users': users,
                'info': info,
            }
            if cards:
                for card in cards:
                    if card.get('card_style') == 1:
                        card_group = card.get('card_group')
                        for i in card_group:
                            if i.get('card_type') == 42:
                                info.append(i.get('desc'))
                    elif not card.get('card_style'):
                        card_group = card.get('card_group')
                        for i in card_group:
                            if i.get('card_type') == 10:
                                user = i.get('user')
                                users.append(user)
            if mode == MODE_FANS:
                since_id = cardlistInfo.get('since_id')
                ret.update({
                    'next': since_id,
                })
            containerid = cardlistInfo.get('containerid')
            ret.update({
                'uid': containerid.split('_-_')[-1],
                'users': users,
                'timestamp': int(time.time() * 1000),
            })
            return ret
        
        return inner
    
    return wrapper


def user_tweets_extractor(mode=MODE_M):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            data: dict = func(*args, **kwargs)
            cards_data: dict = data.get('data')
            if not cards_data:
                print(data)
            if mode == MODE_M:
                cards: list = cards_data.get('cards')
                cardlistInfo: dict = cards_data.get('cardlistInfo')
                # 采集since_id用于翻页
                if not cardlistInfo:
                    return {}
                since_id = cardlistInfo.get('since_id')
                total = cardlistInfo.get('total')
                # 只采集微薄，不采集话题以及感兴趣的人推荐等类型
                cards = [i for i in cards if i['card_type'] == 9]
                for i in cards:
                    mblog = i.get('mblog')
                    mblog.pop('user')
                    i.update({
                        'total': total,
                        'since_id': since_id,
                        'timestamp': int(time.time() * 1000),
                    })
            elif mode == MODE_WEB:
                cards: list = cards_data.get('list')
                total = cards_data.get('total')
                since_id = cards_data.get('since_id')
                bottom_tips_visible = cards_data.get('bottom_tips_visible')
                if bottom_tips_visible:
                    since_id = None
                    total = cards_data.get('bottom_tips_text')
                    log.warning(f'提示:{total}, 当前请求 uid: {args[1]}')
                for i in cards:
                    i.pop('user')
                    i.update({
                        'total': total,
                        'since_id': since_id,
                        'timestamp': int(time.time() * 1000),
                    })
            else:
                raise Exception(f'用户微博解析模式无效.无效模式：{mode}')
            if not cards:
                log.warning(f'【模式：{mode}】当前未采集到微博数据，返回结果:{data}')
                return {}
            
            return cards
        
        return inner
    
    return wrapper


def user_info_extractor(mode=MODE_M):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            data: dict = func(*args, **kwargs)
            profile = data.get('data')
            if mode == MODE_M:
                userInfo: dict = profile.get('userInfo')
                tabsInfo: dict = profile.get('tabsInfo')
                # 获取对应的containerid用于针对性的采集相应菜单下的微薄
                tabs = tabsInfo.get('tabs')
                tabs = [
                    {
                        "key": i['tabKey'],
                        "containerid": i['containerid'],
                    }
                    for i in tabs]
            elif mode == MODE_WEB:
                userInfo = profile.get('user')
                tabs = None
            else:
                log.error(f'无效的返回数据:{data}')
                raise Exception('无效的返回数据')
            user_info = {
                'uid': userInfo.get('id'),
                'nickname': userInfo.get('screen_name'),
                'gender': userInfo.get('gender'),
                'domain': userInfo.get('domain'),
                'description': userInfo.get('description'),
                'mblog_count': userInfo.get('statuses_count'),
                'follow_count': userInfo.get('follow_count') or userInfo.get('friends_count'),
                'fans_count': userInfo.get('followers_count'),
                'svip': userInfo.get('svip'),
                'mbrank': userInfo.get('mbrank'),
                'mbtype': userInfo.get('mbtype'),
                'urank': userInfo.get('urank'),
                'user_type': userInfo.get('user_type'),
                'location': userInfo.get('location'),
                'weihao': userInfo.get('weihao'),
                'wenda': userInfo.get('wenda'),
                'is_star': userInfo.get('is_star'),
                'is_muteuser': userInfo.get('is_muteuser'),
                'verified': userInfo.get('verified'),
                'verified_type': userInfo.get('verified_type'),
                'verified_type_ext': userInfo.get('verified_type_ext'),
                'verified_reason': userInfo.get('verified_reason'),
                'profile_url': userInfo.get('profile_url'),
                'sina_blog_url': userInfo.get('url'),
                'avtar': userInfo.get('avatar_hd') or userInfo.get('profile_image_url'),
                'background_image': userInfo.get('cover_image_phone'),
                'tabs': tabs,
                'timestamp': int(time.time() * 1000),  # 采集时间戳
            }
            
            return user_info
        
        return inner
    
    return wrapper


def user_details_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        data: dict = func(*args, **kwargs)
        details: dict = data.get('data')
        labels = details.get('label_desc', [])
        label_desc = []
        for i in labels:
            label_desc.append({"name": i.get("name")})
        return {
            "sunshine_credit": details.get('sunshine_credit'),
            "birthday": details.get('birthday'),
            "created_at": details.get('created_at'),
            "location": details.get('location'),
            "ip_location": details.get('ip_location'),
            "education": details.get('education'),
            "career": details.get('career'),
            "company": details.get('company'),
            "label_desc": label_desc,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def hot_topics_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data: dict = response.get('data')
        statuses = data.get('statuses')
        total_data_num = data.get('total_data_num')
        return {
            'topics': statuses,
            'total': total_data_num,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def video_ranks_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        videos_data = data.get('Component_Billboard_Billboardlist')
        videos = videos_data.get('list')
        cursor = videos_data.get('next_cursor')
        update_time = videos_data.get('update_time')
        return {
            'cate_id': args[1],
            'update_date': update_time,
            'next': cursor,
            'videos': videos,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def hot_ranks_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data: dict = response.get('data')
        realtime = data.get('realtime')
        hotgov = data.get('hotgov')
        ads = []
        hots = []
        for i in realtime:
            if i.get('is_ad'):
                ads.append(i)
            else:
                hots.append(i)
        return {
            'hots': hots,
            'hotgov': hotgov,
            'ads': ads,
            'timestamp': time_to_date(time.time(), '%Y-%m-%d %H:%M'),
        }
    
    return inner


def tweet_details_parser(func):
    @wraps(func)
    def inner(*args, **kwargs):
        html = func(*args, **kwargs)
        try:
            html = html[html.find('"status":'):]
            html = html[: html.rfind('"call"')]
            html = html[: html.rfind(",")]
            html = "{" + html + "}"
            js = json.loads(html, strict=False)
            weibo_info = js.get("status")
            if weibo_info:
                weibo_info.update({
                    'timestamp': int(time.time() * 1000),
                })
                return weibo_info
        except Exception as e:
            log.error(f'解析请求返回的html失败:{e}')
            return {}
        else:
            return js
    
    return inner


def tweet_comments_extractor(mode=MODE_WEB, key_total='total_comments_count'):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response: dict = func(*args, **kwargs)
            if not response:
                return {}
            try:
                if mode == MODE_M:
                    response = response.get('data')
                data: dict = response.get('data')
                total = response.get('total_number')
                max_id = response.get('max_id', kwargs.get('since_id', 0) + 1 if kwargs.get('since_id') else None)
                trendsText = response.get('trendsText')
                for i in data:
                    i.update({
                        'root_mid': args[1],
                        key_total: total,
                        'timestamp': int(time.time() * 1000),
                        'next': max_id,
                        'trendsText': trendsText,
                    })
            except Exception as e:
                log.error(f'解析返回结果出错：{e}')
                return {}
            else:
                return data
        
        return inner
    
    return wrapper


def tweet_rewards_parser(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data: dict = response.get('data')
        price_data = data.get('data')
        score_data = data.get('score_data')
        seller_info = data.get('seller_info')
        return {
            'root_mid': args[1],
            'root_user': seller_info.get('uid'),
            'price_fans_list': price_data.get('fans_list'),
            'score_fans_list': score_data.get('fans_list'),
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def pic_tweet_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        pic_list = data.get('pic_list')
        for i in pic_list:
            i.update({
                'keywords': args[1],
                'timestamp': int(time.time() * 1000),
            })
        return pic_list
    
    return inner


def cn_emotions_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        emoticon = data.get('emoticon')
        cn_emo = emoticon.get('ZH_CN')
        return cn_emo
    
    return inner


def display_channels_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        category = data.get('category')
        details = category.get('details')
        return details
    
    return inner


def user_groups_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        join_groups = data.get('join_groups')
        total = data.get('total')
        return {
            'total': total,
            'groups': join_groups,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def stopics_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        count = response.get('count')
        topics = [{
            'title': i.get('title'),
            'image': i.get('image'),
            'description': i.get('description'),
            'is_obturate': i.get('is_obturate'),
            'topic_id': w3lib.url.parse_qsl(i.get('st_url'))[0][-1],
        } for i in data]
        return {
            'total': count,
            'topics': topics,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def super_topics_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        ret = []
        for i in data:
            ret.append({
                'title': i.get('title'),
                'image': i.get('image'),
                'description': i.get('description'),
                'is_obturate': i.get('is_obturate'),
                'topic_id': i.get('act_log').get('oid'),
                'timestamp': int(time.time() * 1000),
            })
        return ret
    
    return inner


def hot_tweet_groups_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        ret = {}
        groups = response.get('groups')
        for i in groups:
            group = i.get('group', [])
            for g in group:
                title = g.get('title')
                gid = g.get('gid')
                containerid = g.get('containerid')
                if containerid and title not in ret:
                    ret.update({
                        title: {
                            'group_id': gid,
                            'containerid': containerid,
                            'title': title,
                        }
                    })
        return ret
    
    return inner


def hot_tweets_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response = func(*args, **kwargs)
        total = response.get('total_number')
        statuses = response.get('statuses')
        for i in statuses:
            i.update({
                'total': total,
                'since_id': response.get('since_id'),
                'next': response.get('max_id'),
                'group_id': kwargs.get('group_id'),
                'timestamp': int(time.time() * 1000),
            })
        return statuses
    
    return inner


def video_stars_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        stars = data.get('Component_Star_List')
        group_name = stars.get('group_name')
        group = stars.get('group')
        single = stars.get('single')
        single_name = stars.get('single_name')
        return {
            group_name: group,
            single_name: single,
            'timestamp': int(time.time() * 1000),
        }
    
    return inner


def video_feed_extractor(key='Component_Home_Recommend'):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response: dict = func(*args, **kwargs)
            data = response.get('data')
            video_data = data.get(key)
            videos = video_data.get('list')
            cursor = video_data.get('next_cursor')
            for i in videos:
                i.update({
                    'next': cursor,
                    'timestamp': int(time.time() * 1000),
                })
            return videos
        
        return inner
    
    return wrapper


def video_channels_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        menu = data.get('Component_Channel_Menu')
        for i in menu:
            i.pop('icon')
        return menu
    
    return inner


def user_friends_tweets(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        statuses = response.get('statuses')
        since_id = response.get('since_id')
        for i in statuses:
            i.update({
                'next': since_id,
                'timestamp': int(time.time() * 1000),
            })
        return statuses
    
    return inner


def user_hots_extractor(key='next_cursor'):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            response: dict = func(*args, **kwargs)
            data = response.get('data')
            hots = data.get('list')
            next_cursor = data.get(key)
            for i in hots:
                i.update({
                    'next': next_cursor,
                    'timestamp': int(time.time() * 1000),
                })
            return hots
        
        return inner
    
    return wrapper


def user_albums_extractor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        response: dict = func(*args, **kwargs)
        data = response.get('data')
        album_list = data.get('album_list')
        return album_list
    
    return inner
