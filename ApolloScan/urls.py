#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-16 20:16:08
#########################################################################

from django.conf.urls import patterns, include, url

side_info = [
    (r'','apollo_logs','日志',{'icon':'fa-dashboard'}),
    (r'test1/','test1','Test1',{'icon':'fa-bar-chart-o'}),
    (r'test2/','test2','Test2',{'icon':'fa-table'}),
]

side_pattern_tuples = [(r'^'+url+'$',view,{'title':title
            ,'sideinfo':side_info}) for (url,view,title,infos) in side_info]

api_pattern_tuples = [(r'^api/$','api_data')]

item_patterns = patterns('ApolloScan.views',*side_pattern_tuples)
api_patterns = patterns('ApolloScan.views',*api_pattern_tuples)

urlpatterns = item_patterns+api_patterns
