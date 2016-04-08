#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-12 19:29:28
#########################################################################
from bson.objectid import ObjectId
from ApolloCommon.annotation import singleton
from . import BaseCardManager

@singleton
class AppCardsManager(BaseCardManager):

    def newest(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)
        cursor = self.db.find({'platform':{'$ne':'Douban'}}).sort([('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        return self.assemble(cursor)

    def action_movie(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)
        cursor = self.db.find({'platform':{'$ne':'Douban'},'tags':'动作'}).sort([('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        return self.assemble(cursor)

    def comedy_movie(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)
        cursor = self.db.find({'platform':{'$ne':'Douban'},'tags':'喜剧'}).sort([('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        return self.assemble(cursor)

    def drama_movie(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)
        cursor = self.db.find({'platform':{'$ne':'Douban'},'tags':'剧情'}).sort([('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        return self.assemble(cursor)

    def top_movie(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)

        result = [];
        cursor = self.db.find({'platform':'Douban'}).sort([('rating_score',-1),('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        for i in cursor:
            item = self.db.find_one({'platform':{'$ne':'Douban'},'douban_id':i['key']})
            if item:
                item['douban_detail'] = i
                result.append(item)
        return self.assemble(result)

    def jp_movie(self,page=1,page_count=15):
        _skip = self.calculate_skip(page,page_count)
        cursor = self.db.find({'platform':{'$ne':'Douban'},'tags':'剧情'}).sort([('timestamp',-1)])\
            .skip(_skip).limit(page_count)
        return self.assemble(cursor)
