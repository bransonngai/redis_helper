# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 20:22:46 2020

@author: bransonngai
"""
import json
import redis
import pickle

from .secret import (
    local_redis_secret,
    algoable_redis_secret,
    cookie_redis_secret,
    local_no_password_secret
)

from BATrader.ba_constants import MachineName, machine_name


class RedisHelper:
    """
    Pub-Sub Model
    
    port:
        connection port
    
    use_strict:
        don't know what this is
    
    db:
        using db0 by default
        
    password:
        equals to AUTH
    """

    def __init__(self,
                 config_name: str = 'local',
                 db=0,
                 use_strict=False,
                 pub_sub_channel='fm104.5',
                 ):

        if config_name == 'local':
            __loaded_config = local_redis_secret
        else:
            if machine_name == MachineName.ALGOABLE:
                print('Running in algoable. Using algoable local redis')
                __loaded_config = algoable_redis_secret
            elif machine_name in [MachineName.TINYA, MachineName.TINYB]:
                __loaded_config = local_no_password_secret

        pool = redis.ConnectionPool(
            db=db,
            host=__loaded_config['db_host'],
            port=__loaded_config['db_port'],
            password=__loaded_config['db_password'],
        )

        if use_strict:
            self.conn = redis.StrictRedis(connection_pool=pool)
        else:
            self.conn = redis.Redis(connection_pool=pool)  # 連接redis服務器

        self.pub_sub_channel = pub_sub_channel  # 訂閱頻道
        self.threads = []  # storing subscribe thread

    def publish(self, msg):  # 定義發佈函數，msg為發佈消息
        return self.conn.publish(self.pub_sub_channel, msg)

    def publish_pyobj(self, msg):  # 定義發佈函數，msg為發佈消息
        return self.conn.publish(self.pub_sub_channel, pickle.dumps(msg))

    def subscribe(self, callback_handler, **kwargs):
        """
        The whole script will get blocked if there are no new messages.
        msg:
            {'type': 'subscribe', 'pattern': None, 'channel': b'fm104.5', 'data': 1}
         {'type': 'message', 'pattern': None, 'channel': b'fm104.5', 'data': b'\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x03abc\x94K{s.'}
        
        """
        sub = self.conn.pubsub()  # 定義接收函數，接收消息
        sub.subscribe(self.pub_sub_channel)

        # 等待消息
        for new_msg in sub.listen():
            callback_handler(new_msg, **kwargs)

    def subscribe_by_thread(self, callback_handler, **kwargs):
        sub = self.conn.pubsub()  # 定義接收函數，接收消息
        sub.subscribe(**{self.pub_sub_channel: callback_handler})
        self.threads.append(sub.run_in_thread(sleep_time=0.001))

    def stop_subscribe(self):
        for t in self.threads:
            t.stop()

    """ 
    Subclass of RedisHelper, 
    Redis database class
    
    sadd:
        將一個或多個 member 元素加入到集合 key 當中
    """

    def set(self, key, value):
        self.conn.set(key, pickle.dumps(value))

    def get(self, key):
        value = self.conn.get(key)
        if value:
            try:
                return pickle.loads(value)
            except AttributeError:
                return ''
        return ''

    def delete(self, key: str):
        self.conn.delete(key)

    def set_list(self, list_name: str, lst: list):
        self.conn.sadd(list_name, *lst)

    def get_list(self, list_name: str):
        return self.conn.smembers(list_name)

    def set_dict(self, dic_name: str, dic: dict):

        try:
            self.conn.hmset(dic_name, dic)
        except redis.exceptions.DataError:
            # It's a complicted dict
            dic = json.dumps(dic)
            self.conn.set(dic_name, dic)

    def get_dict(self, dic_name: str):
        try:
            return self.conn.hgetall(dic_name)
        except redis.exceptions.ResponseError:
            return json.loads(self.conn.get(dic_name))

    def get_value_in_dict(self, dic_name: str, key_to_get: str):

        return self.conn.hmget(dic_name, key_to_get)
        # try:
        #     return self.conn.hgetall(dic_name)
        # except redis.exceptions.ResponseError:
        #     return json.loads(self.conn.get(dic_name))

    def flush_db_redis(self):
        """ Clear everything, needs confirm """
        ans = input('Are you sure ?')
        if ans == 'y':
            self.conn.flushdb()
            print('Flushed.')

_redis_manager: RedisHelper = None

def get_redis_manager():
    global _redis_manager
    if not _redis_manager:
        _redis_manager = RedisHelper()
    return _redis_manager
