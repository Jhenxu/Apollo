# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import logging
import os
import time
import re
from scrapy.log import ScrapyFileLogObserver
from scrapy.spider import BaseSpider
from ApolloCommon import config
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
    def __init__(self, category=None, *args, **kwargs):
        self.logfile = logging_start(self.name)
        self.start_time = time.time()
        super(ApolloSpider, self).__init__(*args, **kwargs)

    def closed(self, reason):
        result = {}
        stat = self.crawler.stats.get_stats()
        duration = time.time() - self.start_time
        result['stat'] = str(stat)
        result['duration'] = int(duration)
        result['fname'] = self.logfile
        result['timestamp'] = self.start_time
        result['platform'] = self.name
        Agent.getAgent().db[config.get('MONGODB_LOG')].insert(result)
