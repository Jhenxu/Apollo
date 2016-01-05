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

@singleton
class MongoAgent(object):
    """
        a singleton mongodb agent
    """
    def __init__(self):
        try:
            MONGODB_SERVER = MongoAgentFactory.MONGODB_SERVER
            MONGODB_PORT = MongoAgentFactory.MONGODB_PORT
            MONGODB_DB = MongoAgentFactory.MONGODB_DB

            client = MongoClient(MONGODB_SERVER,MONGODB_PORT)
            self.db = client[MONGODB_DB]
            self.db[MongoAgentFactory.MONGODB_ITEM].ensure_index('key',unique=True)
        except Exception as e:
            log.msg(str(e),level=log.ERROR)
            traceback.print_exc()

#使用singleton 装饰器后无法直接使用类方法
#    @classmethod
#    def from_crawler(cls,crawler):
#        cls.MONGODB_SERVER = crawler.settings.get('MONGODB_SERVER', 'localhost')
#        cls.MONGODB_PORT = crawler.settings.getint('MONGODB_PORT', 27017)
#        cls.MONGODB_DB = crawler.settings.get('MONGODB_DB', 'youjoy_mongo')

class MongoAgentFactory(object):

    @classmethod
    def from_crawler(cls,crawler):
        cls.MONGODB_SERVER = crawler.settings.get('MONGODB_SERVER', 'localhost')
        cls.MONGODB_PORT = crawler.settings.getint('MONGODB_PORT', 27017)
        cls.MONGODB_DB = crawler.settings.get('MONGODB_DB', 'apollo_db')
        cls.MONGODB_ITEM = crawler.settings.get('MONGODB_ITEM','apollo_item')
        cls.MONGODB_SPIDER = crawler.settings.get('MONGODB_SPIDER','apollo_spider')

    @staticmethod
    def getAgent():
        return MongoAgent()
