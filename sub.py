# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 03:05:14 2020

@author: tHOMAS
"""
from redis_helper import local_instance
import pickle

r = local_instance


# def handler(msg, **kwargs):
    
#     print(pickle.loads(msg['data']))

# r.subscribe_by_thread(handler)


def handler_print(msg):
    print(msg)

r.subscribe_by_thread(handler_print)