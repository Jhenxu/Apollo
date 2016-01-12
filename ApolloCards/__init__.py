#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 17:43:40
#########################################################################
from ApolloCommon.mongodb import MongoAgentFactory
from ApolloCommon import config
from bson.objectid import ObjectId
from ApolloCommon.annotation import singleton

@singleton
class CardsManager(object):

    def __init__(self):
        self.db = MongoAgentFactory.getAgent().db[config.get('MONGODB_ITEM','apollo_item')]

    def newest(self,page=1):
        if page < 1:
            page = 1
        if not isinstance(page,int):
            try:
                page = int(page)
            except:
                page = 1
                
        _skip = (page-1)*15
        cursor = self.db.find({'platform':{'$ne':'Douban'}}).sort([('years',-1),('timestamp',-1)])\
            .skip(_skip).limit(15)
        result = []
        for item in cursor:
            if 'douban_item' in item and isinstance(item['douban_item'],ObjectId):
                dou_item = self.db.find_one({'_id':item['douban_item']})
                if dou_item:
                    item['douban_detail'] = dou_item
                result.append(self._assemble(item))
            else:
                result.append(self._assemble(item))
        return result

    def _assemble(self,item):
        r = {}
        r['title'] = item['title']
        r['years'] = item['years']
        r['timestamp'] = item['timestamp']
        if 'douban_detail' in item:
            r['rating_score'] = item['douban_detail']['rating_score']
        #     r['img'] = ''
        # else:
        #     r['img'] = ''

        return r
