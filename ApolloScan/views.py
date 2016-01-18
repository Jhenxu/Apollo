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

        def compare(x, y):
            #按照文件插入时间倒序
            stat_x = os.stat(os.path.join(_log_dir, x))
            stat_y = os.stat(os.path.join(_log_dir, y))
            if stat_x.st_ctime < stat_y.st_ctime:
                return 1
            elif stat_x.st_ctime > stat_y.st_ctime:
                return -1
            else:
                return 0

        if os.path.isdir(_log_dir) and os.path.exists(_log_dir):
            _log_list = os.listdir(_log_dir)
            _log_list.sort(compare)
            for _file_name in _log_list:
                _regex = r'^(?P<date>.*?)_(?P<time>.*?)_(?P<platform>.*?).log$'
                m = re.match(_regex,_file_name)
                item = {}
                if m:
                    _file_path = os.path.join(_log_dir, _file_name)
                    _file_stat = os.stat(_file_path)
                    format_time = m.group('date') + ' ' +m.group('time')
                    item['file_size'] = _file_stat.st_size
                    item['time'] = format_time
                    item['file'] = _file_name
                    item['platform'] = m.group('platform')
                    data.append(item)
        result['data'] = data
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse("No action.")
