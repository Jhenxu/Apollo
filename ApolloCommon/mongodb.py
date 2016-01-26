#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2014-01-31 12:46:06
#########################################################################
import traceback
import pymongo

from scrapy import log
from pymongo.connection import MongoClient
from annotation import singleton
from . import config

@singleton
class MongoAgent(object):
    """
        a singleton mongodb agent
    """
    def __init__(self):
        try:
            MONGODB_SERVER = config.get('MONGODB_SERVER', 'localhost')
            MONGODB_PORT = config.get('MONGODB_PORT', 27017)
            MONGODB_DB = config.get('MONGODB_DB', 'apollo_db')

            client = MongoClient(MONGODB_SERVER,MONGODB_PORT)
            self.colletcion = client[MONGODB_DB]
            self.colletcion[config.get('MONGODB_ITEM','apollo_item')].ensure_index('key',unique=True)
        except Exception as e:
            log.msg(str(e),level=log.ERROR)
            traceback.print_exc()

class ApolloItemCollectionWarpper(object):
    '''装饰apollo_item采集器'''
    def __init__ (self, func):
        self.func = func
        for name in set(dir(func)) - set(dir(self)):
            setattr(self, name, getattr(func, name))

    def __call__ (self, *args):
        return self.func(*args)

    def find_one(self, *args, **kargs):
        condition = {}
        condition['status'] = {'$ne':10}#尚未激活
        if len(args) > 0:
            condition.update(args[0])
        return self.func.find_one(condition, **kargs)

    def find(self, *args, **kargs):
        condition = {}
        condition['status'] = {'$ne':10}#尚未激活
        if len(args) > 0:
            condition.update(args[0])
        return self.func.find(condition, **kargs)

class MongoAgentFactory(object):
    apollo_db = None

    @staticmethod
    def getDB():
        if None == MongoAgentFactory.apollo_db:
            db = MongoAgent().colletcion[config.get('MONGODB_ITEM')]
            MongoAgentFactory.apollo_db = ApolloItemCollectionWarpper(db)
        return MongoAgentFactory.apollo_db

    @staticmethod
    def getNoWarpDB():
        return MongoAgent().colletcion[config.get('MONGODB_ITEM')]

    @staticmethod
    def getLogDB():
        return MongoAgent().colletcion[config.get('MONGODB_LOG')]

    @staticmethod
    def getSpiderDB():
        return MongoAgent().colletcion[config.get('MONGODB_SPIDER')]
