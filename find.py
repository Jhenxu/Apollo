#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: find.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-06 02:44:35
#########################################################################
import pymongo
from pymongo.connection import MongoClient

db = MongoClient('localhost',27017)['apollo_db']['apollo_item']

print '豆瓣未获取条目数量:'+str(db.find({'$where': 'this.douban_id == ""'}).count())
print str(db.find({'$where': 'this.douban_id == ""'}).count()) +'/'+str(db.find().count())

for item in db.find({'$where': 'function() {\
        function arrayContains(needle, arrhaystack){ return (arrhaystack.indexOf(needle) > -1);}\
        return (\
        this.years >= 2010 \
        && (arrayContains("美国",this.tags) || arrayContains("日本",this.tags) ||arrayContains("韩国",this.tags))\
        && this.douban_score > 8.0\
        )}'}).sort([('douban_score',pymongo.DESCENDING),('years',pymongo.DESCENDING)]):
    print '%s 年份:%s 豆瓣:%s'%(item['name'].encode('utf-8','ignore'),str(item['years']),str(item['douban_score']))
    print '   标签：'+' '.join(x.encode('utf-8','ignore') for x in item['tags'])
    index = 0
    for d in item['torrents']:
        if index == 0:
            print '   种子:'+d['torrent_file_name'].encode('utf-8','ignore')
        else:
            print '       '+d['torrent_file_name'].encode('utf-8','ignore')
        index += 1
    print '====='*20
