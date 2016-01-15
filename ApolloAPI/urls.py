#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-16 01:48:12
#########################################################################
from django.conf.urls import patterns, include, url
api_group = [
        (r'^test$','test'),
        (r'^query$','query'),
        (r'^download$','download'),
    ]
urlpatterns = patterns('ApolloAPI.views.api',*api_group)
