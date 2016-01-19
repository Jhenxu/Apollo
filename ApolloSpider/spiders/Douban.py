#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-03 14:37:10
#########################################################################
import json,traceback,time
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from ApolloSpider.items import DoubanItem
from scrapy.contrib.spidermiddleware.httperror import HttpError
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config
from . import logging_start

class DoubanSpider(BaseSpider):
    name        = 'Douban'

    def __init__(self, category=None, *args, **kwargs):
        logging_start(self.name)
        super(DoubanSpider, self).__init__(*args, **kwargs)

    def set_crawler(self, crawler):
        super(DoubanSpider, self).set_crawler(crawler)
        crawler.settings.overrides['DOWNLOAD_DELAY'] = 3.5
        crawler.settings.overrides['RANDOMIZE_DOWNLOAD_DELAY'] = True

    def start_requests(self):
        db = Agent.getAgent().db[config.get('MONGODB_ITEM','apollo_item')]
        banlist = [item['id'] for item in Agent.getAgent().db[config.get('MONGODB_SPIDER','apollo_spider')].find({'platform':self.name,'action':'movie_not_found'})]

        for item in db.find({'douban_item':{'$exists':False},'douban_id':{'$exists':True}},fields=['douban_id','_id']):
            if not item['douban_id'] == None and not '' == item['douban_id'] and not '0' == item['douban_id']:
                if not item['douban_id'] in banlist:
                    api = 'https://api.douban.com/v2/movie/subject/'+item['douban_id']
                    req = Request(url=api,callback=self.parse,dont_filter=True\
                        ,errback = lambda e: self.parse_error(e, item))
                    req.meta['_id'] = item['_id']
                    yield req
                else:
                    log.msg('Ban douban id:'+item['douban_id'],level=log.DEBUG)

        def _reparse_douban(update_time,ratings_count,year,retries):
            diffts = time.time()-update_time
            year_anchor = int(time.strftime("%Y", time.localtime(time.time()))) - year+1
            max_rc = 20/year_anchor
            if max_rc < 5:
                max_rc = 5
            if retries > max_rc:
                return False

            anchor = 24*60*60*year_anchor
            if ratings_count < 100:
               return diffts > 3*anchor
            elif ratings_count < 500:
               return diffts > 7*anchor
            elif ratings_count < 1000:
               return diffts > 10*anchor
            elif ratings_count < 2000:
               return diffts > 15*anchor

        reparseitems = []
        for item in db.find({'platform':self.name},fields=['ratings_count','year','update','key','retries']):
            rc = 0
            if 'retries' in item:
                rc = item['retries']
            if _reparse_douban(item['update'],item['ratings_count'],item['year'],rc):
                if not item['key'] in banlist:
                    reparseitems.append(item['key'])
                    log.msg('重新爬取DoubanItem:'+str(item['key']),level=log.DEBUG)
                else:
                    log.msg('Ban douban id:'+item['douban_id'],level=log.INFO)
        log.msg('重新爬取Douban:'+str(len(reparseitems)),level=log.INFO)
        for _id in reparseitems:
            api = 'https://api.douban.com/v2/movie/subject/'+_id
            req = Request(url=api,callback=self.parse,dont_filter=True\
                ,errback = lambda e: self.parse_error(e, item))
            req.meta['_id'] = None
            yield req

    def parse(self,response):
        item  = DoubanItem(self.name)
        jitem = json.loads(response.body)
        item['apollo_item'] = response.meta['_id']
        item['key'] = jitem['id']
        item['summary'] = jitem['summary'].encode('utf-8','ignore')
        item['img_ore'] = jitem['images']['large'].encode('utf-8','ignore')
        item['rating_score'] = float(jitem['rating']['average'])
        item['ratings_count'] = jitem['ratings_count']
        try:
            item['year'] = int(jitem['year'])
        except:
            item['year'] = 0
            log.msg('发生错误：%s'%traceback.format_exc(),level=log.ERROR)
        item['mobile_url'] = jitem['mobile_url'].encode('utf-8','ignore')
        item['content'] = response.body
        yield item

# msg: "You API access rate limit has been exceeded. Contact api-master@douban.com if you want higher limit. ",
# code: 1998,
# request: "GET /v2/movie/subject/4011211"
    def parse_error(self,failure,src_item):
        if isinstance(failure.value, HttpError):
            response = failure.value.response
            log.msg('访问失败：status=%s %s'%(response.status,response.url),level=log.ERROR)
            try:
                jitem = json.loads(response.body)
                if 'code' in jitem and 'msg' in jitem:
                    if jitem['code'] == 1998:
                        raise CloseSpider('豆瓣访问受限...')
                        log.msg('访问受限：%s %s'%(jitem['code'],jitem['msg'].encode('utf-8','ignore')),level=log.ERROR)
                    elif 5000 == jitem['code']:#movie not found
                        sp = response.url.split('/')
                        _id = sp[len(sp)-1]
                        if len(_id) > 0:
                            item = {}
                            item['platform'] = self.name
                            item['action'] = 'movie_not_found'
                            item['id'] = _id
                            Agent.getAgent().db[config.get('MONGODB_SPIDER','apollo_spider')].insert(item)
                        log.msg('%s %s'%(jitem['code'],jitem['msg'].encode('utf-8','ignore')),level=log.ERROR)
                    else:
                        log.msg('发生错误：%s %s'%(jitem['code'],jitem['msg'].encode('utf-8','ignore')),level=log.ERROR)
            except ValueError:
                log.msg('发生错误：%s'%traceback.format_exc(),level=log.ERROR)


        if isinstance(failure.value,Exception):
            try:
                raise failure.value
            except:
                tb = traceback.format_exc()
            finally:
                log.msg('发生错误：%s'%tb,level=log.ERROR)
