#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 17:43:40
#########################################################################
import json
from ApolloCommon.mongodb import MongoAgentFactory
from ApolloCommon import config,class_for_name
from bson.objectid import ObjectId

_app_cards_info = ('ApolloCards.managers','AppCardsManager')

def call_card(key):
    mod_name = _app_cards_info[0]
    cls_name = _app_cards_info[1]
    mgr = class_for_name(mod_name,cls_name)
    fuc = key
    return getattr(mgr,fuc)

class BaseCardManager(object):

    def __init__(self):
        self.db = MongoAgentFactory.getDB()

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
            r['alias'] = item['alias']
            r['directors'] = []
            r['starring'] = []
            r['banid'] = item['douban_id']
            r['mid'] = str(item['_id'])
            r['imdb'] = item['imdb']

            if 'douban_detail' in item:
                _dou_item = item['douban_detail']
                r['rating_score'] = _dou_item['rating_score']
                # if 'img' in _dou_item and len(_dou_item['img'])>0:
                #     r['img'] = '/%s/thumbs/mobile/%s'%(_dou_item['platform'],_dou_item['img'])
                r['summary'] = _dou_item['summary']

                info = json.loads(_dou_item['content'])

                if 'images' in info and info['images'] and 'medium' in info['images']:
                    r['img'] = info['images']['medium']

                def _assemble_star(item):
                    result = {}
                    result['name'] = item['name']
                    if 'avatars' in item and item['avatars'] and 'medium' in item['avatars']:
                        result['avatar'] = item['avatars']['medium']
                    else:
                        result['avatar'] = ''
                    result['id'] = item['id']
                    return result

                for i in info['directors']:
                    r['directors'].append(_assemble_star(i))

                for i in info['casts']:
                    r['starring'].append(_assemble_star(i))

                if 'genres' in info:
                    r['tags'] = info['genres']

                if 'aka' in info:
                    r['alias'] = info['aka']
            else:
                if 'img' in item and len(item['img'])>0:
                    r['img'] = '/%s/thumbs/mobile/%s'%(item['platform'],item['img'])

                def _assemble_star(item):
                    result = {}
                    result['name'] = item
                    result['avatar'] = ''
                    result['id'] = ''
                    return result

                for i in item['director']:
                    r['directors'].append(_assemble_star(i))

                for i in item['starring']:
                    r['directors'].append(_assemble_star(i))

            if not 'img' in r:
                r['img'] = ''

            # r['torrents'] = []
            # for t in item['torrents']:
            #     if len(t) > 0:
            #         r['torrents'].append(t)
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
