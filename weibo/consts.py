#!/usr/bin/python
# coding:utf-8


class VideoRanking:
    ALL = 4418213501411061
    FOOD = 4418219809678881
    GAME = 4418219809678883
    MUSIC = 4418219809678875
    CARS = 4418219805484549
    TRAVEL = 4418219805484537
    SPORTS = 4418219809678887
    COMIC = 4418219809678867
    KNOWLEDGE = 4418219809678865
    FUNNY = 4418219809678869
    DANCE = 4418219805484551


class HotTweets:
    HOURS = {
        'group_id': '1028039999',
        'containerid': '102803_ctg1_9999_-_ctg1_9999_home',
    }
    YESTERDAY = {
        'group_id': '1028038899',
        'containerid': '102803_ctg1_8899_-_ctg1_8899',
    }
    BEFORE_YESTERDAY = {
        'group_id': '1028038799',
        'containerid': '102803_ctg1_8799_-_ctg1_8799',
    }
    WEEKS = {
        'group_id': '1028038698',
        'containerid': '102803_ctg1_8698_-_ctg1_8698',
    }
    MAN = {
        'group_id': '1028038998',
        'containerid': '102803_ctg1_8998_-_ctg1_8998',
    }
    LADY = {
        'group_id': '1028038997',
        'containerid': '102803_ctg1_8997_-_ctg1_8997',
    }


class SuperTopics(object):
    RECENTLY = 123333
    LOCAL = 149
    LIVES = 182
    INTERESTS = 148
    STARS = 2
    FAMOUS = 184
    ADVERTISE = 181
    SPORTS = 98
    GAMES = 126
    ESPORTS = 187
    COMICS = 97
    READING = 94
    LEARNING = 133
    CAMPUS = 152
    ENTERPRISE = 183
    WELFARE = 6
    OTHERS = 8


class Visible(object):
    PUBLIC = 0
    FANS = 10
    FRIENDS = 6
    SELF = 1
    GROUPS = 5


class Video(object):
    ORIGINAL = 0  # 原创
    SECOND = 2  # 二创
    REPOST = 1  # 转载
    COPYRIGHT = 3  # 版权


class Types(object):
    GENERAL = 1
    USERS = 3
    REALTIME = 61
    VIDEOS = 64
    CONCERNS = 62
    PICS = 63
    ARTICLES = 21
    HOTS = 60
    TOPICS = 38
    SUPERS = 98
    LOCATIONS = 92
    GOODS = 97
    PAGES = 32
