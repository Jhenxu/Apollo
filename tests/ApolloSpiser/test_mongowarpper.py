#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-08 11:48:24
#########################################################################

import unittest,urllib2,urllib
from bson.objectid import ObjectId
from ApolloCommon.mongodb import MongoAgentFactory as Agent

class TestMongoWarpper(unittest.TestCase):
    def setUp(self):
        print 'setUp'

    def test_mongowarpper(self):
        conditions = [
            {'_id':ObjectId('567f92112f1b6216b9a5cbd8')},
            {'platform':{'$ne':'Douban'}},
            {'platform':{'$ne':'Douban'},'tags':'动作'},
            {'platform':{'$ne':'Douban'},'tags':'喜剧'},
            {'platform':{'$ne':'Douban'},'tags':'剧情'},
            {'platform':'Douban'},
        ]

        for condition in conditions:
            s1 = Agent.getDB().find(condition).count()
            condition['status'] = {'$ne':10}
            s2 = Agent.getNoWarpDB().find(condition).count()
            print '%s %d %d'%(str(condition),s1,s2)
            self.assertTrue(s1 > 0)
            self.assertTrue(s1 == s2)

        s1 = Agent.getDB().find_one(fields=['title'])
        s2 = Agent.getNoWarpDB().find_one(fields=['title'])
        print '%s %d %d'%('fields=[title]',len(s1),len(s2))
        self.assertTrue(len(s1) == 2)
        self.assertTrue(len(s1) == len(s2))

    def tearDown(self):
        print 'tearDown'

if __name__=='__main__':
    unittest.main()
