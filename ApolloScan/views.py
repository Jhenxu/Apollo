#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-16 20:16:08
#########################################################################
import json
import functools
import os
import re
import time
import datetime
from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config

def requestWrap(call_method):
    @functools.wraps(call_method)
    def wrapper(*args, **kwargs):
        def _inject_selected(name,sideinfo):
            for url,method,title,infos in sideinfo:
                if method == name:
                    infos['selected'] = True
                else:
                    infos['selected'] = False
            return sideinfo

        if 'sideinfo' in kwargs:
            _inject_selected(call_method.__name__,kwargs['sideinfo'])
        return call_method(*args, **kwargs)
    return wrapper

@requestWrap
def apollo_logs(request,sideinfo,title):
    data = {}
    data['title'] = title
    data['sidebar_items'] = [(url,title,infos) for (url,method,title,infos) in sideinfo]
    return render_to_response('log.html',data)

@requestWrap
def test1(request,sideinfo,title):
    data = {}
    data['title'] = title
    data['sidebar_items'] = [(url,title,infos) for (url,method,title,infos) in sideinfo]
    return render_to_response('scan_page.html',data)

@requestWrap
def test2(request,sideinfo,title):
    data = {}
    data['title'] = title
    data['sidebar_items'] = [(url,title,infos) for (url,method,title,infos) in sideinfo]
    return render_to_response('scan_page.html',data)

def api_data(request):
    action = request.GET.get('action','')
    _log_dir = os.path.join(os.getcwd(), 'logs')
    if 'getlog' == action:
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
    elif 'loglist' == action:
        result = {}
        data = []
        _db = Agent.getAgent().db[config.get('MONGODB_LOG')]
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
    return HttpResponse("No action.")
