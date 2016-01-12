#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 22:54:47
#########################################################################
from ApolloCards import CardsManager

cm = CardsManager()
for item in cm.newest():
    r = {}
    r['title'] = item['title']
    r['years'] = item['years']
    r['timestamp'] = item['timestamp']
    if 'douban_detail' in item:
        r['rating_score'] = item['douban_detail']['rating_score']
    print r
