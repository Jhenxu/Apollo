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
from ApolloCards import CardsManager

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
    }
    return (action in action_command),action_command.get(action,'')

def _homepage(request):
    # cm = CardsManager()
    # return cm.newest()
    return 'homepage'

def _test(request):
    cm = CardsManager()
    _page = request.GET.get('page',1)
    return cm.newest(page=_page)
