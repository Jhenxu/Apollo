#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-04 17:37:25
#########################################################################
import hashlib
import os
from ApolloSpider.utils import isFileExpire
from ApolloSpider.pipelines import check_spider_pipeline
from scrapy import log
from scrapy.http import Request
from scrapy.exceptions import DropItem
from scrapy.contrib.pipeline.files import FileException, FilesPipeline
from scrapy.utils.request import request_fingerprint
from ApolloCommon.torrentparse import TorrentParser

class NotorrentsDrop(DropItem):
    """Product with no torrent exception"""


class TorrentException(FileException):
    """General torrent error exception"""


class TorrentPipeline(FilesPipeline):
    """Abstract pipeline that implement the image thumbnail generation logic
    """

    MEDIA_NAME = 'torrent'

    @classmethod
    def from_settings(cls, settings):
        cls.EXPIRES = settings.getint('TORRENT_EXPIRES', 90)
        cls.FILE_EXPIRES = settings.getint('FILE_EXPIRES',0)
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        cls.STORE_URI = settings['TORRENTS_STORE']
        return cls(cls.STORE_URI)

    @check_spider_pipeline
    def process_item(self, item, spider):
        reqs = [req for req in item.get('torrents_reqs', [])]
        reqs2 =[]
        for r in reqs:
            fname = self.STORE_URI+self.file_path(r)
            if isFileExpire(fname,expire=self.FILE_EXPIRES):
                reqs2.append(r)
                log.msg('种子文件过期或不存在:'+fname,level=log.DEBUG)
        if len(reqs2) > 0:
            item['torrents_reqs'] = []
            #不能直接赋值，否则为[]?
            for req in reqs2:
                item['torrents_reqs'].append(req)
            return super(TorrentPipeline,self).process_item(item, spider)
        else:
            log.msg('种子请求不存在:'+str(item['title'].encode('utf-8')),level=log.DEBUG)
            return item

    def get_media_requests(self, item, info):
        return [req for req in item.get('torrents_reqs', [])]

    def item_completed(self, results, item, info):
        for _info in [x for ok, x in results if ok]:
            _file = _info['path']
            _path = os.path.join(self.STORE_URI,_file)
            if os.path.exists(_path):
                log.msg('种子下载完成:'+_file,level=log.INFO)
                print _path
                try:
                    tp = TorrentParser(_path)
                except Exception:
                    tp = None
                    log.msg('解析种子错误.'+traceback.format_exc(),level=log.ERROR)
                if tp.is_torrent():
                    _key = 'torrents_downloaded'
                    info.spider.crawler.stats.inc_value(_key)
                    item['torrents'].append(_file)
                else:
                    _key = 'torrents_checkdown_failed'
                    info.spider.crawler.stats.inc_value(_key)
                    os.remove(_path)
                    log.msg('下载完成，但种子校验失败:[%s][%s]'%(_file,_info['url']),level=log.WARNING)
        return item

    def media_to_download(self, request, info):
        return super(TorrentPipeline,self).media_to_download(request,info)

    def media_failed(self, failure, request, info):
        _key = 'torrents_failed'
        info.spider.crawler.stats.inc_value(_key)
        return super(TorrentPipeline,self).media_failed(failure,request,info)

    def media_downloaded(self, response, request, info):
        return super(TorrentPipeline,self).media_downloaded(response,request,info)

    def file_path(self, request, response=None, info=None):
        ## start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('TorrentPipeline.file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        ## end of deprecation warning block
        return request.meta['torrent_file_name']
