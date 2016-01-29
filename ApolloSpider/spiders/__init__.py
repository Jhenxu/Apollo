#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-03 14:37:10
#########################################################################

import logging
import os
import time
from scrapy.log import ScrapyFileLogObserver
from scrapy import log
from scrapy.spider import BaseSpider
from ApolloCommon.mongodb import MongoAgentFactory as Agent

def logging_start(spider):
    if not os.path.exists('./logs/'):
        os.makedirs('./logs/')
    _ts = int(time.time())
    log = '%s_%s.log' % (time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(_ts)),spider)
    logfile = open('logs/'+log, 'w')
    log_observer = ScrapyFileLogObserver(logfile, level=logging.INFO)
    log_observer.start()
    return log

class ApolloSpider(BaseSpider):
    info = {}
    complete = False
    FULL_SPIDER = False

    def set_crawler(self, crawler):
        super(BaseSpider, self).set_crawler(crawler)
        self.TS_ITEM_DEEP_SPIDER = crawler.settings.getint('APOLLO_ITEM_DEEP_SPIDER',0)*24*60*60
        self.TS_SPIDER_EXPIRED_DAYS = crawler.settings.getint('APOLLO_FULL_SPIDER',0)*24*60*60

        self.spider_item = Agent.getSpiderDB().find_one({'platform':self.name})
        self.full_spder_key = 'FullSpider_'+self.name
        self.ful_spider_item = Agent.getSpiderDB().find_one({'platform':self.full_spder_key})
        if not self.ful_spider_item == None:
            ts = self.ful_spider_item['lastime']
            if self.TS_SPIDER_EXPIRED_DAYS < 0:
                self.FULL_SPIDER = False
            else:
                self.FULL_SPIDER = (time.time()-(ts-1)) > self.TS_SPIDER_EXPIRED_DAYS
        else:
            self.FULL_SPIDER = True

    def __init__(self, category=None, *args, **kwargs):
        self.logfile = logging_start(self.name)
        self.start_time = time.time()
        super(ApolloSpider, self).__init__(*args, **kwargs)


    def closed(self, reason):
        if self.complete:
            self._store_spider_info()
        if self.FULL_SPIDER:
            self._store_ful_spider()
        self._store_stat()

    def isFullSpder(self):
        return self.FULL_SPIDER

    def _store_ful_spider(self):
        if None == self.ful_spider_item:
            data = {}
            data['platform'] = self.full_spder_key
            data['lastime'] = time.time()
            Agent.getSpiderDB().insert(data)
        else:
            mogon_id = self.ful_spider_item['_id']
            data = {}
            data['lastime'] = time.time()
            Agent.getSpiderDB().update({'_id':mogon_id},{'$set':data})
        log.msg('更新FullSpiderItem.[%s]'%str(self.name),level=log.INFO)

    def _store_spider_info(self):
        self.info['platform'] = self.name
        self.info['lastime'] = time.time()
        if None == self.spider_item:
            Agent.getSpiderDB().insert(self.info)
            log.msg('更新SpiderItem.[%s]'%str(self.info),level=log.INFO)
        else:
            mogon_id = self.spider_item['_id']
            Agent.getSpiderDB().update({'_id':mogon_id},{'$set':self.info})
            log.msg('更新SpiderItem.[%s]'%str(self.info),level=log.INFO)

    def _store_stat(self):
        result = {}
        stat = self.crawler.stats.get_stats()
        duration = time.time() - self.start_time
        result['stat'] = str(stat)
        result['duration'] = int(duration)
        result['fname'] = self.logfile
        result['timestamp'] = self.start_time
        result['platform'] = self.name
        Agent.getLogDB().insert(result)
