# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 20:22:46 2020

@author: tHOMAS
"""
import json
import pickle
from socket import gethostname

import redis

from .secret import local_redis_secret, algoable_redis_secret, cookie_redis_secret, local_no_password_secret
from BATrader.ba_constants import MachineName


# Redis holds key:value pairs , support GET, SET and DEL and serveral additional commands
# Keys are always strings
# values can be different data types

# MSET Lebanon Beirut Norway Oslo France Paris
# MGET Lebanon Norway Bahamas

# HSET realpython url "https://realpython.com/"
# HSET realpython github realpython
# HSET realpython fullname "Real Python"

# HMSET pypa url "https://www.pypa.io/" github pypa fullname "Python Packaging Authority"
# HGETALL pypa

# Hashes, Sets, Lists

def get_local_config():
    if gethostname() == MachineName.ALGOABLE:
        print('Running in algoable. Using algoable local redis')
        return algoable_redis_secret
    elif gethostname() == MachineName.TINYA or gethostname() == MachineName.TINYB:
        return local_no_password_secret
    else:
        return local_redis_secret


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

    def __init__(self, host='localhost',
                 port=6379,
                 use_strict=False,
                 db=0,
                 password=None,
                 ):

        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db,
                                    password=
                                    password)

        if use_strict:
            self.conn = redis.StrictRedis(connection_pool=pool)
        else:
            self.conn = redis.Redis(connection_pool=pool)  # 連接redis服務器

        self.default_pub_sub_channel = 'fm104.5'  # 訂閱頻道
        self.threads = []  # storing subscribe thread

    # def conn(self):
    #     return self.conn

    def publish(self, msg, pub_sub_channel=''):  # 定義發佈函數，msg為發佈消息
        if not pub_sub_channel:
            pub_sub_channel= self.default_pub_sub_channel
        
        self.conn.publish(pub_sub_channel, msg)
        return True

    def publish_pyobj(self, msg, pub_sub_channel=''):  # 定義發佈函數，msg為發佈消息
        if not pub_sub_channel:
            pub_sub_channel= self.default_pub_sub_channel
        self.conn.publish(pub_sub_channel, pickle.dumps(msg))
        return True

    def subscribe(self, callback_handler, pub_sub_channel='', **kwargs):
        """
        The whole script will get blocked if there are no new messages.
        msg:
            {'type': 'subscribe', 'pattern': None, 'channel': b'fm104.5', 'data': 1}
         {'type': 'message', 'pattern': None, 'channel': b'fm104.5', 'data': b'\x80\x04\x95\x0c\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x03abc\x94K{s.'}
        
        """
        if not pub_sub_channel:
            pub_sub_channel = self.default_pub_sub_channel

        sub = self.conn.pubsub()  # 定義接收函數，接收消息
        sub.subscribe(pub_sub_channel)

        # 等待消息

        for new_msg in sub.listen():
            callback_handler(new_msg, **kwargs)

    def test_handler(self, msg):
        print(pickle.loads(msg['data']))

    def subscribe_by_thread(self, callback_handler, pub_sub_channel=self.default_pub_sub_channel, **kwargs):
        sub = self.conn.pubsub()  # 定義接收函數，接收消息
        sub.subscribe(**{pub_sub_channel: callback_handler})
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
            return pickle.loads(value)
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


class LocalConfigRedis(RedisHelper):
    """ Cookie local redis, use on local directly """

    def __init__(self):
        config = get_local_config()
        super(LocalConfigRedis, self).__init__(host=config['db_host'],
                                               port=config['db_port'],
                                               password=config['db_password'])


class CookieConfigRedis(RedisHelper):
    """ Cookie local redis, use on local directly """

    def __init__(self):
        config = cookie_redis_secret
        super(CookieConfigRedis, self).__init__(host=config['db_host'],
                                                port=config['db_port'],
                                                password=config['db_password'])


class RedisWithConfig(RedisHelper):
    """ Cookie local redis, use on local directly """

    def __init__(self, config_name: str):
        config = None
        if config_name == 'algoable':
            config = algoable_redis_secret
        elif config_name == 'cookie':
            config = cookie_redis_secret
        elif config_name == 'local':
            config = local_redis_secret
        else:
            print('CONFIG name no found')
            return

        super(RedisWithConfig, self).__init__(host=config['db_host'],
                                              port=config['db_port'],
                                              password=config['db_password'])


def return_redis_instance_by_name(config_name: str):
    """
    Trying to migrate with Redis

    Redis seems hv securities breach in production server, stop using it first
    """
    return RedisWithConfig(config_name)
