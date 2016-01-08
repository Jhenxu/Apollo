#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: doubanstore.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-08 15:58:12
#########################################################################
import os
import subprocess
from pymongo.connection import MongoClient

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
