#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-04 17:34:37
#########################################################################
import time
import functools
from scrapy import Request,log
from scrapy.contrib.pipeline.images import ImagesPipeline
from ApolloSpider.items import ApolloItem,DoubanItem
from ApolloCommon.mongodb import MongoAgentFactory
from ApolloCommon import config
from ApolloSpider.utils import isFileExpire

#标注的Pipeline.process_item方法将校验是否在spider.pipeline中定义，定义了
#将执行，不定义将跳过
def check_spider_pipeline(process_item_method):
    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if hasattr(spider,'pipeline') and (self.__module__ + "." + self.__class__.__name__) in spider.pipeline:
            spider.log(msg % 'executing', level=log.DEBUG)
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.log(msg % 'skipping', level=log.DEBUG)
            return item

    return wrapper

class ApolloImagePipline(ImagesPipeline):

    @classmethod
    def from_settings(cls, settings):
        cls.FILE_EXPIRES = settings.getint('FILE_EXPIRES',0)
        cls.MIN_WIDTH = settings.getint('IMAGES_MIN_WIDTH', 0)
        cls.MIN_HEIGHT = settings.getint('IMAGES_MIN_HEIGHT', 0)
        cls.EXPIRES = settings.getint('IMAGES_EXPIRES', 90)
        cls.THUMBS = settings.get('IMAGES_THUMBS', {})
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']

        cls.IMAGES_URLS_FIELD = settings.get('IMAGES_URLS_FIELD', cls.DEFAULT_IMAGES_URLS_FIELD)
        cls.IMAGES_RESULT_FIELD = settings.get('IMAGES_RESULT_FIELD', cls.DEFAULT_IMAGES_RESULT_FIELD)
        cls.STORE_URI = settings['IMAGES_STORE']
        return cls(cls.STORE_URI)

    def process_item(self, item, spider):
        _img_url = ''
        if 'img_ore' in item and len(item['img_ore']) > 0:
            _img_url = item['img_ore']

        if not _img_url == None and not '' == _img_url:
            req = self._build_request(_img_url,item['platform'])
            filepath = self.STORE_URI+self.file_path(req)
            if isFileExpire(filepath,expire=self.FILE_EXPIRES):
                log.msg('准备下载图片:'+filepath,level=log.INFO)
                return ImagesPipeline.process_item(self, item, spider)
            else:
                return item
        else:
            log.msg('无法获取图片下载地址:'+str(item['title'].encode('utf-8')),level=log.INFO)
            return item

    def _build_request(self,url,platform='Default'):
        req = Request(url)
        req.meta['platform'] = str(platform.encode('utf-8'))
        return req

    def get_media_requests(self, item, info):
        _img_url = item['img_ore']
        _platform = item['platform']
        return self._build_request(_img_url,platform=_platform)

    def file_path(self, request, response=None, info=None):
        path = super(ApolloImagePipline,self).file_path(request, response=response, info=info)
        return request.meta['platform']+'/'+path

    def thumb_path(self, request, thumb_id, response=None, info=None):
        path = super(ApolloImagePipline,self).thumb_path(request, thumb_id, response=response, info=info)
        return request.meta['platform']+'/'+path

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            log.msg('Item contains no images.',level=log.WARNING)
            return item
        path = image_paths[0].split('/')
        path = path[len(path)-1]
        item['img'] = path
        return item

class MongodbPipeline(object):
    def __init__(self):
        self.db = MongoAgentFactory.getAgent().db

    def process_item(self,item,spider):
        return self._process_db(item,spider)

    def _process_db(self,item,spider):
        if isinstance(item,ApolloItem):
            return self._process_apollo(item,spider)
        elif isinstance(item,DoubanItem):
            return self._process_douban(item,spider)

    def _process_apollo(self,item,spider):
        _db = self.db[config.get('MONGODB_ITEM','apollo_item')]
        dbItem = _db.find_one({'key':item.getKey()},fields=['torrents','torrents_size'])
        if not dbItem == None:
            if len(item.get('torrents',[])) > 0:
                for n in item.get('torrents',[]):
                    dbItem['torrents'].append(n)
                dbItem['torrents_size'] = len(dbItem.get('torrents',[]))
                update_dict = {'torrents':dbItem['torrents']\
                        ,'torrents_size':len(dbItem.get('torrent',[]))\
                        ,'timestamp':time.time()}
                result = _db.update({'_id':dbItem['_id']},{'$set':update_dict})
                log.msg('更新条目:'+str(item['title'].encode('utf-8')),level=log.DEBUG)
            else:
                log.msg('已经是最新的条目:'+str(item['title'].encode('utf-8')),level=log.DEBUG)
        else:
            detail = item.toDBItem()
            detail['ins_ts'] = time.time()
            if 'douban_id' in item and not item['douban_id'] == None and not '' == item['douban_id'] and not '0' == item['douban_id']:
                r = _db.find_one({'platform':'Douban','key':item['douban_id']})
                if r:
                    detail['douban_item'] = r['_id']
            result = _db.insert(detail)
            if len(item.get('torrents',[])) == 0:
                log.msg('未获取种子:'+str(item['title'].encode('utf-8')),level=log.WARNING)
            log.msg('插入新条目:'+str(item['title'].encode('utf-8')),level=log.INFO)
        return item

    def _process_douban(self,item,spider):
        _db = self.db[config.get('MONGODB_ITEM','apollo_item')]
        dbItem = _db.find_one({'key':item['key']})

        def update_apollo_item(result):
            if result and 'apollo_item' in item and not None == item['apollo_item']:
                _db.update({'_id':item['apollo_item']},{'$set':{'douban_item':result}})
                log.msg('更新条目:'+str(item['apollo_item']),level=log.INFO)

        if not dbItem == None:
            result = _db.update({'_id':dbItem['_id']},{'$set':item.toDBItem()})
            update_apollo_item(result)
            log.msg('更新Douban条目:'+str(item['key'].encode('utf-8')),level=log.INFO)
        else:
            result = _db.insert(item.toDBItem())
            update_apollo_item(result)
            log.msg('插入新Douban条目:'+str(item['key'].encode('utf-8')),level=log.INFO)
        return item
