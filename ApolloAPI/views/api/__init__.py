#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-08 23:07:58
#########################################################################
import json
from django.http import HttpResponse
from ApolloCards import call_card
from ApolloCommon.mongodb import MongoAgentFactory
from bson.objectid import ObjectId
from Fortune import today

def test(request):
    resp = {}
    resp['status'] = 200
    resp['msg'] = 'hello api!'
    return HttpResponse(json.dumps(resp), content_type="application/json")

def query(request):
    isOK,result = _dispatch_action(request)
    resp = {}
    if isOK:
        resp['status'] = 200
        resp['msg'] = ''
        resp['data'] = result
    else:
        resp['status'] = 301
        resp['msg'] = '无法识别action'
        resp['data'] = {}

    return HttpResponse(json.dumps(resp), content_type="application/json")

def download(request):
    mid = request.GET.get('mid','')
    resp = {}
    if mid and len(mid)>0:
        resp['status'] = 200
        resp['msg'] = ''
        item = MongoAgentFactory.getDB().find_one({'_id':ObjectId(mid)})
        result = {}
        result['torrents'] = []
        for t in item['torrents']:
            if len(t) > 0:
                result['torrents'].append(t)
        resp['data'] = result
    else:
        resp['status'] = 302
        resp['msg'] = '无法获取mid'
        resp['data'] = {}
    return HttpResponse(json.dumps(resp), content_type="application/json")

#http://127.0.0.1:8188/api/fortune?action=today
def fortune(request):
    isOK,result = _dispatch_fortune(request)
    resp = {}
    if isOK:
        resp['status'] = 200
        resp['msg'] = ''
        resp['data'] = result
    else:
        resp['status'] = 301
        resp['msg'] = '无法识别action'
        resp['data'] = {}
    return HttpResponse(json.dumps(resp,ensure_ascii=False), content_type="application/json")

def _dispatch_fortune(request):
    action = request.GET.get('action','')
    action_command = {
        'today':today(request),
    }
    return (action in action_command),action_command.get(action,'')


def _dispatch_action(request):
    action = request.GET.get('action','')
    action_command = {
        'homepage':_homepage(request),
        'test':_test(request),
        'list':_list(request),
    }
    return (action in action_command),action_command.get(action,'')

def _homepage(request):
    result = {}
    result['hasMore'] = True
    result['sections'] = []
    result['tabs'] = _getTabs()
    _cards = ('top_movie','action_movie','comedy_movie','drama_movie','sup_newest')
    for card in _cards:
        _r = {}
        _r['celltype'] = card
        _r['modules'] = call_card(card)(page_count=8)
        result['sections'].append(_r)

    card = 'list'
    _r = {}
    _r['celltype'] = card
    _r['modules'] = call_card('newest')(page=1)
    result['sections'].append(_r)

    return result

def _list(request):
    _page = request.GET.get('page',1)
    _type = request.GET.get('type','')
    result = {}
    result['hasMore'] = True
    if '' != _type:
        result['modules'] = call_card(_type)(page=_page)
    return result

def _getTabs():
    result = []
    result.append({'navName':'最新影视','action':'newest'})
    result.append({'navName':'日剧','action':'sup_newest'})
    result.append({'navName':'动作片','action':'action_movie'})
    result.append({'navName':'剧情片','action':'drama_movie'})
    result.append({'navName':'喜剧片','action':'comedy_movie'})
    return result

def _test(request):
    _page = request.GET.get('page',1)
    return call_card('sup_newest')(page=_page)
