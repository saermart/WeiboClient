#!/usr/bin/python
# coding:utf-8

import threading
from inspect import isfunction

import pymongo

# sql语句与MongoDB语句的映射
con_map = {
    '=': '$eq',
    '<': '$lt',
    '<=': '$lte',
    '>': '$gt',
    '>=': '$gte',
    '!=': '$ne',
}


class Database(object):
    instance_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """
        利用线程锁，实现多线程下的单例模式
        """
        if not hasattr(Database, '_instance'):
            with Database.instance_lock:
                Database._instance = object.__new__(cls)
        return Database._instance
    
    def __init__(self, settings: dict):
        self.host = settings['host']
        self.port = settings['port']
        self.user = settings['user']
        self.passwd = settings['password']
        self.db = settings['database']
        self.conn = None
        self.connected = False
        self.handler = None
        self.table = settings.get('table')
    
    def connect(self):
        """
        连接MongoDB
        """
        self.conn = pymongo.MongoClient(f'mongodb://{self.host}:{self.port}')
        self.handler = self.conn[self.db]
        if self.user and self.passwd:
            self.conn.get_database(self.db).authenticate(self.user, self.passwd)
        self.connected = True
    
    def close(self):
        """
        关闭数据库连接
        """
        self.conn.close()
        self.conn = None
        self.connected = False
    
    def use_db(self, dbname):
        """
        连接数据库后使用名为dbname的数据库
        :param dbname: 要使用的数据库
        """
        self.handler = self.conn[dbname]
    
    def save(self, data, tname=None, format=None):
        """
        保存数据到数据集
        :param data: 要保存的数据,{}类型或 [{},{}..]类型
        :param tname: 数据集(collection)
        :param format:对数据进行格式化的函数，可以根据数据结构自定义
        """
        table = self.table if self.table else tname
        format = None if not isfunction(format) else format
        if not table:
            raise Exception('No table or data collection specified by tname.')
        if isinstance(data, dict):
            data = format(data) if format else data
            self.handler[table].insert_one(data)
        elif isinstance(data, list):
            for i in data:
                if isinstance(i, dict):
                    i = format(i) if format else i
                    self.handler[table].insert_one(i)
                else:
                    raise TypeError('Expected a dict type value inside the list,%s type received.' % type(data))
        else:
            raise TypeError('Expected a [{},{}..] or {} type data,%s type received.' % type(data))
    
    def select(self, condition, tname=None, sort=None, c_map=True):
        table = self.table if self.table else tname
        if not isinstance(condition, dict):
            raise TypeError('condition is not a valid dict type param.')
        else:
            try:
                if c_map:
                    conditions = self.__gen_mapped_condition(condition)
                else:
                    conditions = condition
                if sort and isinstance(sort, dict):
                    res = self.handler[table].find(condition).sort(list(sort.items()))
                else:
                    res = self.handler[table].find(conditions)
                data = list(res)
                return data if data else []
            except Exception as e:
                print('Error class : %s , msg : %s ' % (e.__class__, e))
                return
    
    def delete(self, condition, tname=None):
        if not condition: return
        conditions = self.__gen_mapped_condition(condition)
        table = self.table if self.table else tname
        if not isinstance(condition, dict):
            raise TypeError('condition is not a valid dict type param.')
        self.handler[table].delete_many(conditions)
    
    def update(self, condition, data, tname=None):
        table = self.table if self.table else tname
        if not data: return
        if not isinstance(condition, dict) and not isinstance(data, dict):
            raise TypeError('Params (condition and data) should both be the dict type.')
        conditions = self.__gen_mapped_condition(condition)
        self.handler[table].update(conditions, {'$set': data}, False, True)
    
    def all(self, tname=None):
        table = self.table if self.table else tname
        data = list(self.handler[table].find())
        return data
    
    def __gen_mapped_condition(self, condition):
        for key in condition:
            if isinstance(condition[key], dict):
                t = condition[key]
                operator = list(t.keys())[0]
                value = t[operator]
                o = con_map[operator]
                condition[key].pop(operator)
                condition[key][o] = value
        return condition
