#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2017-01-16 11:14:42
#########################################################################
import time
from ApolloWeird.common.mongodb import MongoAgentFactory

def today(request):
    date = time.strftime('%Y%m%d',time.localtime(time.time()))
    db = MongoAgentFactory.getDB()
    cursor = db.find({'date':date})
    result = {}
    if cursor:
        data = []
        for item in cursor:
            star = {}
            star['star'] = item['star']
            star['date'] = item['date']
            star['fortune'] = item['fortunePart']
            star['part'] = item['secPart']
            data.append(star)
        result['data'] = data

    return result
