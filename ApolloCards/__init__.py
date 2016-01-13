#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 17:43:40
#########################################################################
from ApolloCommon.mongodb import MongoAgentFactory
from ApolloCommon import config,class_for_name
from bson.objectid import ObjectId

_app_cards_info = ('ApolloCards.managers','AppCardsManager')
CARDS_CONF = {
    'newest_mov':(_app_cards_info,'newest'),
    'act_mov':(_app_cards_info,'action_movie'),
    'comedy_mov':(_app_cards_info,'comedy_movie'),
    'drama_mov':(_app_cards_info,'drama_movie'),
    'top_mov':(_app_cards_info,'top_movie'),
    }


def card_method(key):
    t = CARDS_CONF.get(key)
    mod_name = t[0][0]
    cls_name = t[0][1]
    mgr = class_for_name(mod_name,cls_name)
    fuc = t[1]
    return getattr(mgr,fuc)

class BaseCardManager(object):

    def __init__(self):
        self.db = MongoAgentFactory.getAgent().db[config.get('MONGODB_ITEM','apollo_item')]

    def calculate_skip(self,page,page_count):
        if page < 1:
            page = 1
        if not isinstance(page,int):
            try:
                page = int(page)
            except:
                page = 1

        _skip = (page-1)*page_count
        return _skip

    def assemble(self,cursor):

        def _assemble_item(item):
            r = {}
            r['title'] = item['title']
            r['years'] = item['years']
            r['timestamp'] = item['timestamp']
            r['summary'] = ''
            r['tags'] = item['tags']
            if 'douban_detail' in item:
                _dou_item = item['douban_detail']
                r['rating_score'] = _dou_item['rating_score']
                if 'img' in _dou_item and len(_dou_item['img'])>0:
                    r['img'] = '/%s/thumbs/mobile/%s'%(_dou_item['platform'],_dou_item['img'])
                r['summary'] = _dou_item['summary']
            else:
                if 'img' in item and len(item['img'])>0:
                    r['img'] = '/%s/thumbs/mobile/%s'%(item['platform'],item['img'])
            if not 'img' in r:
                r['img'] = ''

            r['torrents'] = []
            for t in item['torrents']:
                if len(t) > 0:
                    r['torrents'].append(t)
            return r

        result = []
        if cursor:
            for item in cursor:
                if not 'douban_detail' in item and 'douban_item' in item\
                        and isinstance(item['douban_item'],ObjectId):
                    dou_item = self.db.find_one({'_id':item['douban_item']})
                    if dou_item:
                        item['douban_detail'] = dou_item
                    result.append(_assemble_item(item))
                else:
                    result.append(_assemble_item(item))
        return result
