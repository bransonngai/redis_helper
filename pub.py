# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 03:02:38 2020

@author: bransonngai
"""
from redis_helper import local_instance

r = local_instance

r.publish_pyobj({'abc': 123})