#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-16 20:16:08
#########################################################################
import functools
from django.shortcuts import render_to_response

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
def activation(request,sideinfo,title):
    data = {}
    data['title'] = title
    data['sidebar_items'] = [(url,title,infos) for (url,method,title,infos) in sideinfo]
    return render_to_response('activation.html',data)
