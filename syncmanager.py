#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: doubanstore.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-08 15:58:12
#########################################################################
import os
import time
import datetime
import re
import subprocess
from pymongo.connection import MongoClient
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config

#nohup scrapy crawl BTtiantang >/dev/null 2>&1 &

def locale_douban_store():
    client = MongoClient('localhost',27017)
    db = client['apollo_db']['apollo_item']

    item = db.find_one({'platform':'Douban'})
    del item['_id']
    s = str(item)
    d = eval(s)

    f1 = 'douban.backup'
    f2 = 'douban.backup_1'

    if os.path.isfile(f1):
       os.remove(f1)

    if os.path.isfile(f2):
       os.remove(f2)

    _file = open(f2,'a')

    for item in db.find({'platform':'Douban'}):
       del item['_id']
       print 'store '+item['key']
       _file.write(str(item)+'\n')

    os.rename(f2,f1)

def upload_douban_store():
    command = 'scp douban.backup admin@123.56.89.33:Apollo/'
    subprocess.call(command,shell=True)
    command = 'scp -r images/Douban/ admin@123.56.89.33:Apollo/images/'
    subprocess.call(command,shell=True)

def sync_locale_store():
    _backup_file = 'douban.backup'
    if not os.path.isfile(_backup_file):
        raise Exception('备份文件不存在.')

    client = MongoClient('localhost',27017)
    db = client['apollo_db']['apollo_item']

    for line in open(_backup_file,'r').readlines():
        d = eval(line)
        c = db.find({'platform':d['platform'],'key':d['key']}).count()
        if c > 0:
            print '本地数据库已经存在 '+d['key'].encode('utf-8')
        else:
            result = db.insert(d)
            for item in db.find({'douban_item':{'$exists':False},'douban_id':d['key']}):
                db.update({'_id':item['_id']},{'$set':{'douban_item':result}})
                print '   更新Item '+item['_id'].encode('utf-8')
            print '插入Item '+d['key'].encode('utf-8')

def sync_log():
    _log_dir = os.path.join(os.getcwd(), 'logs')
    _db = Agent.getAgent().db[config.get('MONGODB_LOG')]

    def compare(x, y):
        #按照文件插入时间升序
        stat_x = os.stat(os.path.join(_log_dir, x))
        stat_y = os.stat(os.path.join(_log_dir, y))
        if stat_x.st_ctime < stat_y.st_ctime:
            return -1
        elif stat_x.st_ctime > stat_y.st_ctime:
            return 1
        else:
            return 0

    if os.path.isdir(_log_dir) and os.path.exists(_log_dir):
        _log_list = os.listdir(_log_dir)
        _log_list.sort(compare)
        for _file_name in _log_list:
            rc = _db.find({"fname":_file_name}).count()
            if rc > 0:
                print 'Has Exist '+_file_name
                continue
            result = {}
            _regex = r'^(?P<date>.*?)_(?P<time>.*?)_(?P<platform>.*?).log$'
            m = re.match(_regex,_file_name)
            item = {}
            if m:
                result['platform'] = m.group('platform')

            _file_path = os.path.join(_log_dir, _file_name)
            _file = open(_file_path,'r')
            data =  _file.read()
            _regex_scrapy_stat = r'Dumping Scrapy stats:\n\t(?P<stat>{[\s\S]*?})'
            f = re.search(_regex_scrapy_stat,data)
            if f:
                stat = eval(f.group('stat').replace('\n','').replace('\t',''))
                duration = time.mktime(stat['finish_time'].timetuple()) -time.mktime(stat['start_time'].timetuple())
                result['stat'] = str(stat)
                result['duration'] = int(duration)
                result['fname'] = _file_name
                result['timestamp'] = int(time.mktime(stat['start_time'].timetuple()))
                status = _db.insert(result)
                print 'Insert '+str(status)

if __name__ == '__main__':
    sync_log()
