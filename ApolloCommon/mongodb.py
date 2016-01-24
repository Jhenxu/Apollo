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

class MongoAgentFactory(object):
    @staticmethod
    def getAgent():
        return MongoAgent()

    @staticmethod
    def getDB():
        return MongoAgent().colletcion[config.get('MONGODB_ITEM','apollo_item')]

    @staticmethod
    def getLogDB():
        return MongoAgent().colletcion[config.get('MONGODB_LOG')]

    @staticmethod
    def getSpiderDB():
        return MongoAgent().colletcion[config.get('MONGODB_SPIDER')]
