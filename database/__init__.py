#!/usr/bin/python
# coding:utf-8

from logging import getLogger

import config
from database.mongo import Database

log = getLogger(__name__)
MONGODB = Database(config.MONGO)
MONGODB.connect()


def save_into_mongo(mongo: Database = MONGODB,
                    dbName: str = None,
                    collectionName: str = None,
                    differ: str or list = None):
    def wrapper(func):
        def inner(*args, **kwargs):
            
            def save(db_instance, data, differ_key, collection):
                if isinstance(differ_key, list):
                    condition = {}
                    for i in differ_key:
                        if '.' in i:
                            keys = i.split('.')
                            m = data
                            for item in keys:
                                m = m.get(item)
                            condition.update({i: {"=": m}})
                        else:
                            condition.update({i: {"=": data.get(i)}})
                else:
                    if '.' in differ_key:
                        keys = differ_key.split('.')
                        m = data
                        for item in keys:
                            m = m.get(item)
                        condition = {differ_key: {"=": m}}
                    else:
                        condition = {differ_key: {"=": data.get(differ_key)}}
                fetched = db_instance.select(condition, tname=collection)
                if fetched:
                    return data
                db_instance.save(data, tname=collection)
                log.info(f'表：{collection} -> 保存数据 {len(data)} 条.')
            
            data = func(*args, **kwargs)
            
            if not data:
                return {}
            collection = kwargs.get('collectionName', collectionName)
            into_mongo = kwargs.get('into_mongo', collection)
            db_name = kwargs.get('dbName', dbName)
            db_instance = kwargs.get('db_instance', mongo)
            differ_key = kwargs.get('differ', differ)
            if not db_instance \
                or not isinstance(db_instance, Database) \
                or not into_mongo \
                or not collection:
                return data
            if db_name:
                db_instance.use_db(db_name)
            else:
                db_instance.use_db(config.MONGO['database'])
            
            if isinstance(data, list):
                for i in data:
                    save(db_instance, i, differ_key, collection)
            else:
                save(db_instance, data, differ_key, collection)
            
            return data
        
        return inner
    
    return wrapper
