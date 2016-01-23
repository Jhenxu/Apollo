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
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from ApolloSpider.items import DoubanItem
from scrapy.contrib.spidermiddleware.httperror import HttpError
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config
from . import ApolloSpider

class DoubanSpider(ApolloSpider):
    name        = 'Douban'

    def set_crawler(self, crawler):
        super(DoubanSpider, self).set_crawler(crawler)
        crawler.settings.overrides['DOWNLOAD_DELAY'] = 3.5
        crawler.settings.overrides['RANDOMIZE_DOWNLOAD_DELAY'] = True

    def start_requests(self):
        db = Agent.getAgent().db[config.get('MONGODB_ITEM','apollo_item')]
        banlist = [item['id'] for item in Agent.getAgent().db[config.get('MONGODB_SPIDER')].find({'platform':self.name,'action':'movie_not_found'})]
        search_banlist = []
        for m in Agent.getAgent().db[config.get('MONGODB_SPIDER')].find({'platform':self.name,'action':'search_no_match'}):
            if m['count'] > 10:
                search_banlist.append(m['item_id'])
                continue
            d = (time.time() - m['timestamp'])/(60*60*24)
            if d < 7:
                search_banlist.append(m['item_id'])

        for item in db.find({'platform':{'$ne':'Douban'},'douban_item':{'$exists':False}},fields=['douban_id','_id','title','starring','director']):
            if not 'douban_id' in item or item['douban_id'] == None or '' == item['douban_id'] or '0' == item['douban_id']:
                if not str(item['_id']) in search_banlist:
                    api = 'https://api.douban.com/v2/movie/search?q='+item['title']
                    req = Request(url=api,callback=self.parsesearch,dont_filter=True\
                        ,errback = lambda e: self.parse_error(e, item))
                    req.meta['item'] = item
                    yield req
                else:
                    log.msg('SearchBan apolloItem id:'+str(item['_id']),level=log.DEBUG)
            else:
                if not item['douban_id'] in banlist:
                    api = 'https://api.douban.com/v2/movie/subject/'+item['douban_id']
                    req = Request(url=api,callback=self.parse,dont_filter=True\
                        ,errback = lambda e: self.parse_error(e, item))
                    req.meta['item'] = item
                    yield req
                else:
                    log.msg('Ban douban id:'+item['douban_id'],level=log.DEBUG)

        def _reparse_douban(update_time,ratings_count,year,retries):
            diffts = time.time()-update_time
            year_anchor = int(time.strftime("%Y", time.localtime(time.time()))) - year+1
            g = lambda x : 1 if x < 1 else x
            year_anchor = g(year_anchor)
            max_rc = int(20/year_anchor)
            g = lambda x : 5 if x < 5 else x
            max_rc = g(max_rc)

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
                    log.msg('Ban douban id:'+item['key'],level=log.INFO)
        log.msg('重新爬取Douban:'+str(len(reparseitems)),level=log.INFO)
        for _id in reparseitems:
            api = 'https://api.douban.com/v2/movie/subject/'+_id
            req = Request(url=api,callback=self.parse,dont_filter=True\
                ,errback = lambda e: self.parse_error(e, item))
            req.meta['item'] = None
            yield req

    def parse(self,response):
        item = self._package_item(response.body)
        item['apollo_item'] = response.meta['item']
        yield item

    def parsesearch(self,response):
        subject,_id = self._match_subject(response)
        if not None == subject:
            self.crawler.stats.inc_value('found_douban_id')
            apollo_item = response.meta['item']
            apollo_item['douban_id'] = _id
            api = 'https://api.douban.com/v2/movie/subject/'+apollo_item['douban_id']
            req = Request(url=api,callback=self.parse,dont_filter=True\
                ,errback = lambda e: self.parse_error(e, apollo_item))
            req.meta['item'] = apollo_item
            yield req

    def _match_subject(self,response):
        item = response.meta['item']
        jitem = json.loads(response.body)
        for sub in jitem['subjects']:
            match = False
            g = lambda k,di:di[k] if k in di else []
            #导演match
            if len(item['director']) > 0:
                for director in g('directors',sub):
                    if director['name'] in item['director']:
                        match = True
                        log.msg('%s 导演匹配'%(item['title'].encode('utf-8')),level=log.INFO)
                        return (json.dumps(sub),sub['id'])
            #演员match
            if len(item['starring']) > 0:
                for avatar in g('casts',sub):
                    if avatar['name'] in item['starring']:
                        match = True
                        log.msg('%s 演员匹配'%(item['title'].encode('utf-8')),level=log.INFO)
                        return (json.dumps(sub),sub['id'])

        _spider_db = Agent.getAgent().db[config.get('MONGODB_SPIDER')]
        m = _spider_db.find_one({'platform':self.name,'action':'search_no_match','item_id':str(item['_id'])})
        if m:
            _id = m['_id']
            del m['_id']
            m['timestamp'] = time.time()
            m['count'] += 1
            _spider_db.update({'_id':_id},{'$set':m})
            log.msg('%s 更新Banlist [%d]'%(item['title'].encode('utf-8'),m['count']),level=log.INFO)
        else:
            ban_item = {}
            ban_item['platform'] = self.name
            ban_item['action'] = 'search_no_match'
            ban_item['item_id'] = str(item['_id'])
            ban_item['timestamp'] = time.time()
            ban_item['count'] = 1
            _spider_db.insert(ban_item)
            log.msg('%s 插入Banlist'%(item['title'].encode('utf-8')),level=log.INFO)
        log.msg('%s 无法匹配'%(item['title'].encode('utf-8')),level=log.INFO)
        return (None,None)

    def _package_item(self,body):
        item  = DoubanItem(self.name)
        jitem = json.loads(body)
        item['key'] = jitem['id']
        item['summary'] = jitem['summary'].encode('utf-8','ignore')
        item['img_ore'] = jitem['images']['large'].encode('utf-8','ignore')
        item['rating_score'] = float(jitem['rating']['average'])
        item['ratings_count'] = jitem['ratings_count']
        try:
            item['year'] = int(jitem['year'])
        except:
            item['year'] = 0
            log.msg('发生错误：%s'%traceback.format_exc(),level=log.WARNING)
        item['mobile_url'] = jitem['mobile_url'].encode('utf-8','ignore')
        item['content'] = body
        return item

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
                            Agent.getAgent().db[config.get('MONGODB_SPIDER')].insert(item)
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
