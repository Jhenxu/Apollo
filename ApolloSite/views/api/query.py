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
from ApolloCards import card_method

def test(request):
    resp = {}
    resp['status'] = 200
    resp['msg'] = 'hello api!'
    return HttpResponse(json.dumps(resp), content_type="application/json")

def homepage(request):
    resp = {}
    resp['status'] = 200
    resp['msg'] = 'hello homepage!'
    print '#### '+str(request)
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
        resp['data'] = ''

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
    result['newest_mov'] = card_method('newest_mov')(page_count=5)
    result['top_mov'] = card_method('top_mov')(page_count=5)
    result['act_mov'] = card_method('act_mov')(page_count=5)
    result['comedy_mov'] = card_method('comedy_mov')(page_count=5)
    result['drama_mov'] = card_method('drama_mov')(page_count=5)
    return result

def _test(request):
    _page = request.GET.get('page',1)
    return card_method('newest_mov')(page=_page)

def _test2(request):
    _page = request.GET.get('page',1)
    return card_method('top_mov')(page=_page)

def _test3(request):
    _page = request.GET.get('page',1)
    return card_method('act_mov')(page=_page)
