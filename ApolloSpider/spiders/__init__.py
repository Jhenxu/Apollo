# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import logging
import time
from scrapy.log import ScrapyFileLogObserver

def logging_start(spider):
    log = 'logs/%s_%s.log' % (time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(int(time.time()))),spider)
    logfile = open(log, 'w')
    log_observer = ScrapyFileLogObserver(logfile, level=logging.INFO)
    log_observer.start()
