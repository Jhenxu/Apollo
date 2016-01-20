#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-03 14:37:10
#########################################################################
import re,random,time
from scrapy import log
from scrapy.spider import BaseSpider
from scrapy.http import Request,FormRequest
from ApolloSpider.items import ApolloItem
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config
from . import ApolloSpider

class BTtiantangSpider(ApolloSpider):
    pipeline = set([
        'ApolloSpider.pipelines.TorrentPipeline.TorrentPipeline',
    ])

    name        = 'BTtiantang'
    BASE_URL    = 'http://www.bttiantang.com/'
    start_urls  = [BASE_URL]
    FULL_SPIDER = False
    complete    = False
    fin_page    = 0
    climbpage  = 0

    def set_crawler(self, crawler):
        super(BTtiantangSpider, self).set_crawler(crawler)
        self.ITEM_DEEP_SPIDER = crawler.settings.getint('APOLLO_ITEM_DEEP_SPIDER',0)
        self.SPIDER_EXPIRED_DAYS = crawler.settings.getint('APOLLO_FULL_SPIDER',0)

    def parse(self,response):
        self.spider_item = Agent.getAgent().db[config.get('MONGODB_SPIDER','apollo_spider')].find_one(\
                {'platform':self.name},fields=['lastime','endpage'])

        _end_regex = '<li><a href=\'/\?PageNo=(\d*?)\'>末页</a></li>'
        self._end_page = int(re.findall(_end_regex,response.body)[0])+1
        expired = False
        if not self.spider_item == None:
            expired = (time.time()-(self.spider_item['lastime']-1)) > self.SPIDER_EXPIRED_DAYS*24*60*60

        if self.spider_item == None or expired:
            log.msg('进入完全爬取模式[spider_item is None [%s] expired=%s].'\
                %(str(self.spider_item == None),expired),level=log.INFO)
            self.FULL_SPIDER = True
            self.climbpage = self._end_page
        else:
            self.climbpage = self._end_page - self.spider_item['endpage']+2
            log.msg('进入半爬取模式.[%d]'%self.climbpage,level=log.INFO)

        for page in range(1,self.climbpage):
        # for page in range(1,80):
            pageUrl = self.BASE_URL+'?PageNo='+ str(page)
            yield Request(url=pageUrl,callback=self.parsePage,dont_filter=True)

        # test = ['http://www.bttiantang.com/subject/27526.html'
        #     ,'http://www.bttiantang.com/subject/27392.html']
        # for url in test:
        #     yield Request(url,callback=self.parseItem,dont_filter=True)

    def parsePage(self,response):
        self.fin_page += 1
        _item_url_regex = '</span><a href="/subject/(.*?)" target="_blank">'
        for url in re.findall(_item_url_regex,response.body):
            itemUrl = self.BASE_URL+'subject/'+url
            yield Request(url=itemUrl,callback=self.parseItem,dont_filter=True)

    def parseItem(self,response):
        _item = ApolloItem('BTtiantang')

        _title_regex = '<div class="moviedteail_tt"><h1>(.*?)</h1><span>(.*?)</span></div>'
        r = re.findall(_title_regex,response.body)
        _item['title'] = '%s'%(r[0][0])

        #获取又名，标签，地区，年份，导演，编剧，主演，imdb
        def parse(tagName):
            _regex_li = r'<li>%s:(.*?)</li>'%tagName
            _regex_tag = r'<a title=".*?" target="_blank" href=".*?">(?P<tag>.*?)</a>'
            tags = []
            item = re.search(_regex_li,response.body)
            if item:
                for r in re.findall(_regex_tag,item.group(1)):
                    if not r == None and not '' == r:
                        tags.append(r)
            return tags

        _item['alias'] = parse('又名')
        _item['tags'] = parse('标签')
        _item['area'] = parse('地区')
        b = parse('年份')
        try:
            if len(b) > 0:
                _item['years'] = int(b[0])
            else:
                _item['years'] = 0
        except ValueError:
            _item['years'] = 0
        _item['director'] = parse('导演')
        _item['screenwriter'] = parse('编剧')
        _item['starring'] = parse('主演')
        b = parse('imdb')
        if len(b) > 0:
            _item['imdb'] = b[0]
        else:
            _item['imdb'] = ''

        #_regex_douban_score = r'<p class="rt" title="豆瓣评分"><strong>(?P<i>\d*?)</strong><em class="dian">.</em><em class="fm">(?P<d>\d*?)</em><em class="fm">分</em></p>'
        #p = re.search(_regex_douban_score,response.body)
        #if p:
        #    _item['douban_score'] = float('%s.%s'%(p.group('i'),p.group('d')))
        #else:
        #    _item['douban_score'] = 0.0

        _regex_douban_jump = r'<a href="(?P<url>.*?)" rel="nofollow" target="_blank" title="去豆瓣查看影片介绍"><em class="e_db"></em></a>'
        p = re.search(_regex_douban_jump,response.body)
        if p:
            _item['meta']['douban'] = self.BASE_URL+p.group('url')

        _regex_img = r'<div class="moviedteail_img">\s+<a class="pic".*?src="(?P<url>.*?)" onerror.*?</a>'
        p = re.search(_regex_img,response.body)
        if p:
            _item['img_ore'] = p.group('url')

        dbItem = Agent.getAgent().db[config.get('MONGODB_ITEM','apollo_item')].find_one(\
                {'key':_item.getKey()},fields=['douban_id','timestamp','torrents_size','years'])
        _item['meta']['dbItem'] = dbItem

        if not None == dbItem and dbItem['torrents_size'] > 0 \
                and (time.time()-dbItem['timestamp']) < (self.ITEM_DEEP_SPIDER*24*60*60):
            log.msg('跳过种子获取.[%s]'%response.url,level=log.DEBUG)
            yield self._relay_douban(_item)
        else:
            isPass = False #是否有种子
            _regex_torrent_ore = r'<div class="tinfo">\s+(<a href=".*?</a>)'
            _item['meta']['torrents_count'] = 0

            for f in re.findall(_regex_torrent_ore,response.body):
                _regex_attr = r'<a href="(?P<url>.*?)" title="(?P<title>.*?)" target="_blank"><p class="torrent"><img border="0" src="/style/torrent.gif" style="vertical-align:middle" alt="">.*?<em>(?P<size>.*?)</em>.torrent</p></a>'
                p = re.search(_regex_attr,f)
                if p:
                    isPass = True
                    _content = {}
                    url = self.BASE_URL+p.group('url')
                    title = p.group('title').replace(' ','').replace('/','.') #种子文件名，去掉空格，替换/为.
                    _content['torrent_file_name'] = title+'.torrent'
                    request = Request(url=url,callback=self.parseTorrent,dont_filter=True)
                    request.meta['item'] = _item
                    request.meta['torrent_file_name'] = title+'.torrent'
                    _item['meta']['torrents_parse_count'] = 0
                    _item['meta']['torrents_count'] += 1
                    yield request
            if not isPass:
                log.msg('未捕获到Torrent.[%s]'%response.url,level=log.WARNING)
                yield _item

    def parseTorrent(self,response):
        _item = response.meta['item']
        _torrents_count = _item['meta']['torrents_count']
        _filename = response.meta['torrent_file_name']
        _regex_url = r'<form action="(?P<url>.*?)" method="post">'
        _regex_hidden = r'<input type="hidden" value="(?P<v>.*?)" name="(?P<k>.*?)">'

        def relay():
            _item['meta']['torrents_parse_count'] += 1
            #等到种子都解析完后再处理
            if not _item['meta']['torrents_parse_count'] == _torrents_count:
                return
            yield self._relay_douban(_item)

        p = re.search(_regex_url,response.body)
        if not p:
            log.msg('无法解析Torrent下载地址',level=log.ERROR,status=response.status)
            return relay()
        else:
            downloadUrl = 'http://www.bttiantang.com'+p.group('url')
            params = {'imageField.x':random.randint(1,55)\
                ,'imageField.y':random.randint(1,140)}
            for v,k in re.findall(_regex_hidden,response.body):
                if p:
                    params[k] = v

            download_body = ''
            for k,v in params.iteritems():
                download_body = '%s%s=%s&'%(download_body,k,v)

            if len(download_body) > 0:
                download_body = download_body[0:(len(download_body)-1)]

            download_headers = {
                'Host':'www.bttiantang.com',
                'Connection':'keep-alive',
                'Pragma':'no-cache',
                'Cache-Control':'no-cache',
                'Origin':'http://www.bttiantang.com',
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
                'Content-Type':'application/x-www-form-urlencoded',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
            }

            request = FormRequest(url=downloadUrl,method='POST',headers=download_headers\
                ,body=download_body,dont_filter=True)
            request.meta['torrent_file_name'] = _filename #种子文件名
            _item['torrents_reqs'].append(request)
            return relay()

    def _relay_douban(self,item):
        if 'dbItem' in item['meta']:
            _dbItem = item['meta']['dbItem']
            if not None == _dbItem and 'douban_id' in _dbItem\
                    and not None == _dbItem['douban_id'] and not '' == _dbItem['douban_id']:
                return item
            else:
                req = Request(url=item['meta']['douban'],callback=self.parseDouban,dont_filter=True)
                req.meta['item'] = item
                return req
        else:
            return item

    def parseDouban(self,response):
        _item = response.meta['item']
        _regex_url = r'movie.douban.com/subject/(?P<id>.*?)/";'
        p = re.search(_regex_url,response.body)
        if p:
            _item['douban_id'] = p.group('id')
        else:
            _item['douban_id'] = ''
        yield _item

    def closed(self, reason):
        super(BTtiantangSpider, self).closed(reason)
        if self.fin_page == (self.climbpage-1):
            if None == self.spider_item:
                item = {}
                item['platform'] = self.name
                item['lastime'] = time.time()
                item['endpage'] = self._end_page
                Agent.getAgent().db[config.get('MONGODB_SPIDER','apollo_spider')].insert(item)
                log.msg('更新SpiderItem.[%s]'%str(item),level=log.INFO)
            else:
                self.spider_item['lastime'] = time.time()
                mogon_id = self.spider_item['_id']
                del self.spider_item['_id']
                Agent.getAgent().db[config.get('MONGODB_SPIDER','apollo_spider')].update({'_id':mogon_id},{'$set':self.spider_item})
                log.msg('更新SpiderItem.[%s]'%str(self.spider_item),level=log.INFO)
