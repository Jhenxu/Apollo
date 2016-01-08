
#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: atomcrawl.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-05 17:12:25
#########################################################################
import time,subprocess
from datetime import datetime
from threading import Timer

class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

def scheduler():
    job()
    deltaSec = getDeltaSecs()
    t = Timer(deltaSec, scheduler)
    t.start()


def getDeltaSecs():
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=3, minute=0, second=0, microsecond=0)
    #y=x.replace(day=x.day, hour=x.hour, minute=x.minute+1, second=x.second, microsecond=x.microsecond)
    delta_t=y-x
    secs=delta_t.seconds+1
    return secs

def job():
    print bcolors.HEADER+('Start scrawl job..... %s' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time()))))+bcolors.ENDC
    command = 'scrapy crawl BTtiantang&&scrapy crawl Douban'
    subprocess.call(command,shell=True)
    print bcolors.OKBLUE+'Finish do command.'+bcolors.ENDC

if __name__=='__main__':
    scheduler()

#nohup python atomcrawl.py >/dev/null 2>&1 &
