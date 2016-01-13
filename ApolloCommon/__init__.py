#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 17:32:36
#########################################################################
import importlib

config = {}

config['MONGODB_SERVER'] = 'localhost'
config['MONGODB_PORT'] = 27017
config['MONGODB_DB'] = 'apollo_db'
config['MONGODB_ITEM'] = 'apollo_item'
config['MONGODB_SPIDER'] = 'apollo_spider'
config['IMAGES_STORE'] = './static/images/'
config['TORRENTS_STORE'] = './static/torrents/'

def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c()
