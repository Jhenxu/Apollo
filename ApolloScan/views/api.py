#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-16 20:16:08
#########################################################################
import json
import os
import re
import time
import datetime
from django.http import HttpResponse
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from bson.objectid import ObjectId

def api_data(request):
    action = request.GET.get('action','')
    if 'getlog' == action:
        return getlog(request)
    elif 'loglist' == action:
        return loglist(request)
    elif 'unactivation' == action:
        return getUnactivation(request)
    elif 'active' == action:
        return active(request)
    return HttpResponse("No action.")

def loglist(request):
    _log_dir = os.path.join(os.getcwd(), 'logs')
    result = {}
    data = []
    _db = Agent.getLogDB()
    cursor = _db.find().sort([('timestamp',-1)])
    if cursor:
        for info in cursor:
            _file_name =  info['fname']
            _file_path = os.path.join(_log_dir, _file_name)
            _file_stat = os.stat(_file_path)

            _regex = r'^(?P<date>.*?)_(?P<time>.*?)_(?P<platform>.*?).log$'
            m = re.match(_regex,_file_name)
            item = {}
            if m:
                getRC = lambda k,info:0 if not k in info else info[k]
                _file_path = os.path.join(_log_dir, _file_name)
                _file_stat = os.stat(_file_path)
                format_time = m.group('date') + ' ' +m.group('time')
                size = _file_stat.st_size
                item['file_size'] = str(float((size*10)/1024)/10)+' KB'
                item['time'] = format_time
                item['file'] = _file_name
                item['platform'] = info['platform']
                duration = info['duration']
                _day = lambda x:x/(60*60)
                _min = lambda x:(x%(60*60))/60
                _sec = lambda x:x%60
                _format = lambda d:'%d h %d m %d s'%(_day(duration),_min(duration),_sec(duration)) if _day(duration) > 0 else '%d m %d s'%(_min(duration),_sec(duration))
                item['duration'] = _format(duration)
                error_rc = getRC('log_count/ERROR',eval(info['stat']))
                item['log_error'] = error_rc
                ic = getRC('db_insert_count',eval(info['stat']))
                uc = getRC('db_update_count',eval(info['stat']))
                item['rc_db_changed'] = str(ic)+'/'+str(uc)
                data.append(item)
    result['data'] = data
    return HttpResponse(json.dumps(result), content_type="application/json")

def getlog(request):
    _log_dir = os.path.join(os.getcwd(), 'logs')
    _file_path = os.path.join(_log_dir, request.GET.get('file',''))
    _file = open(_file_path,'r')
    data =  _file.read()
    # _regex_scrapy_stat = r'Dumping Scrapy stats:\n\t(?P<stat>{[\s\S]*?})'
    # f = re.search(_regex_scrapy_stat,data)
    # if f:
    #     stat = eval(f.group('stat').replace('\n','').replace('\t',''))
    #     #print (stat['finish_time'] - stat['start_timme']).total_seconds()
    #     dur = time.mktime(stat['finish_time'].timetuple()) -time.mktime(stat['start_time'].timetuple())
    #     print dur
    #     print type(stat['start_time'])


    htmldata = data.replace('\n','</br>').replace('\t','&nbsp;&nbsp;&nbsp')
    #t = '<html lang="utf-8"><head></head><body><div style="font-size:100px">a</p>a</p>a</p></div></body></html>'

    return HttpResponse(htmldata, content_type="text/plain")

def getUnactivation(request):
    cursor = Agent.getNoWarpDB().find({'status':10},fields=['_id','title','torrents_size','platform','timestamp'])
    result = {}
    data = []
    if cursor:
        for i in cursor:
            item = {}
            item['mid'] = str(i['_id'])
            item['title'] = i['title']
            item['tz'] = i['torrents_size']
            item['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i['timestamp']))
            if 'Suppig' == i['platform']:
                _regex_title_group = r'\[(?P<y>\d\d\d\d)(?P<tag>.*?)\]\[(?P<title>.*?)\]'
                match = re.search(_regex_title_group,i['title'])
                if match:
                    title = match.group('title')
                    title = title.split(' ')[0]
                    item['input'] = title
            data.append(item)
    result['data'] = data
    return HttpResponse(json.dumps(result), content_type="application/json")

def active(request):
    mid = request.GET.get('mid','')
    title = request.GET.get('title','')
    result = {}
    if '' == mid or '' == title:
        result['status'] = 500
    else:
        data = {}
        data['title'] = title
        data['status'] = 0
        data['timestamp'] = time.time()
        r = Agent.getNoWarpDB().update({'_id':ObjectId(mid)},{'$set':data})
        if r:
            result['status'] = 200
        else:
            result['status'] = 401
    return HttpResponse(json.dumps(result), content_type="application/json")
