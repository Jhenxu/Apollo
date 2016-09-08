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
        if item:
            result['torrents'] = item['torrents']
        else:
            result['torrents'] = []

        resp['data'] = result
    else:
        resp['status'] = 302
        resp['msg'] = '无法获取mid'
        resp['data'] = {}
    return HttpResponse(json.dumps(resp), content_type="application/json")


def _dispatch_action(request):
    action = request.GET.get('action','')
    action_command = {
        'homepage':_homepage(request),
        'test':_test(request),
        'test2':_test2(request),
        'test3':_test3(request),
    }
    return (action in action_command),action_command.get(action,'')

def _homepage(request):
    result = {}
    result['hasMore'] = False
    result['sections'] = []
    _cards = ('newest','action_movie','comedy_movie','drama_movie','top_movie')
    for card in _cards:
        _r = {}
        _r['celltype'] = card
        _r['modules'] = call_card(card)(page_count=5)
        result['sections'].append(_r)

    return result

def _test(request):
    _page = request.GET.get('page',1)
    return call_card('newest')(page=_page)

def _test2(request):
    _page = request.GET.get('page',1)
    return call_card('top_movie')(page=_page)

def _test3(request):
    _page = request.GET.get('page',1)
    return call_card('action_movie')(page=_page)
