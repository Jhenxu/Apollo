#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-03 14:37:10
#########################################################################
import re,random,time
import HTMLParser
from scrapy import log
from scrapy.http import Request,FormRequest
from ApolloSpider.items import ApolloItem
from ApolloCommon.mongodb import MongoAgentFactory as Agent
from ApolloCommon import config
from . import ApolloSpider
from scrapy.spider import BaseSpider

class SuppigSpider(ApolloSpider):
    pipeline = set([
        'ApolloSpider.pipelines.TorrentPipeline.TorrentPipeline',
    ])

    name        = 'Suppig'
    BASE_URL    = 'http://www.suppig.net/forum.php?mod=forumdisplay&fid=306'
    PAGE_SIZE = 12#10年以前无法下载
    BAN_TAG = ['预告片']
    fin_page    = 0
    climbpage  = 0

    def start_requests(self):
        if self.isFullSpder():
            self.climbpage = self.PAGE_SIZE
            log.msg('进入完全爬取模式.[%d]'%self.climbpage,level=log.INFO)
        else:
            self.climbpage = 1
            log.msg('进入半爬取模式.[%d]'%self.climbpage,level=log.INFO)

        for n in range(1,(self.climbpage+1)):
            url = self.BASE_URL + ('&page=%d'%n)
            yield self.make_requests_from_url(url)

        # _url = 'http://www.suppig.net/forum.php?mod=viewthread&tid=824632&extra=page%3D14'
        # req = Request(url=_url,callback=self.parseItem,dont_filter=True)
        # req.meta['tid'] = 1125363
        # req.meta['item_name'] = '[2016冬季][别让我走 02][绫濑遥/三浦春马/水川麻美/铃木梨央/麻生祐未]1/24发布'
        # yield req

    def set_crawler(self, crawler):
        super(SuppigSpider, self).set_crawler(crawler)
        self.html_parser = HTMLParser.HTMLParser()

    def parse(self,response):
        self.fin_page += 1
        if self.fin_page == self.climbpage:
            self.complete = True

        _regex_th = r'<th class="(common|new)">([\s\S]*?)</th>'
        _regex_item = r'<a href="(?P<url>.*?)".*?>(?P<item>.*?)</a>'
        content = response.body.decode('gbk','ignore').encode('utf-8')
        for t in re.findall(_regex_th,content):
            t = t[1]
            t = re.sub(r'<em>.*?</em>','', t)
            m = re.search(_regex_item,t)
            if m:
                i = m.group('item')
                if not self._ban(i):
                    # _regex_title_group = r'\[(?P<y>\d\d\d\d)(?P<tag>.*?)\]\[(?P<title>.*?)\]'
                    # match = re.search(_regex_title_group,i)
                    # if match:
                    #     print i
                    #     title =  match.group('title')
                    #     print title.split(' ')[0]
                    _url = self._unescape('http://www.suppig.net/'+m.group('url'))
                    _regex_tid = r'tid=(?P<tid>.*?)&'
                    match = re.search(_regex_tid,_url)
                    if match:
                        tid = match.group('tid')
                        req = Request(url=_url,callback=self.parseItem,dont_filter=True)
                        req.meta['tid'] = tid
                        req.meta['item_name'] = i
                        yield req

    def parseItem(self,response):
        _tid = response.meta['tid']
        _item_name = response.meta['item_name']
        _item = ApolloItem(self.name,prikey=self.name+'_'+str(_tid))
        _item['tags'].append('猪猪乐园')
        ditem = Agent.getDB().find_one({'platform':self.name,'key':_tid})
        if ditem:
            _item['title'] = ditem['title']
        else:
            _item['title'] = _item_name
            _item['status'] = 10 #未激活状态

        content = response.body.decode('gbk','ignore').encode('utf-8')
        _regex_title_group = r'\[(?P<y>\d\d\d\d)(?P<tag>.*?)\]\[(?P<title>.*?)\]'
        m = re.search(_regex_title_group,_item_name)
        if m:
            _item['years'] = int(m.group('y'))
            _item['tags'].append(m.group('tag'))

        def fetch_info(*kargs):
            for key in kargs:
                _regex_director = r''+key+'(:|：)(?P<v>.*?)<'
                m = re.search(_regex_director,content)
                if m:
                    return m.group('v').strip()
            return ''

        def fetch_split(value):
            v = []
            if not None == value and not '' == value:
                for i in value.split('/'):
                    v.append(i.strip())
            return v

        _item['director'] = fetch_split(fetch_info('导演'))
        _item['starring'] = fetch_split(fetch_info('主演','出演'))
        _item['screenwriter'] = fetch_split(fetch_info('编剧'))
        _item['release_date'] = fetch_info('上映日期')
        _item['area'] = '日本'

        _regex_torrent = r'<a href="(.*?)" target="_blank">(.*\.torrent)<\/a>'
        for tor in re.findall(_regex_torrent,content):
            _tor_url = self._unescape('http://www.suppig.net/'+tor[0])
            req = Request(url=_tor_url)
            tor_name = tor[1]
            req.meta['torrent_file_name'] = self._unescape(tor_name)
            _item['torrents_reqs'].append(req)

        _regex_img_area = r'<ignore_js_op>(?P<content>[\s\S]*?)</ignore_js_op>'
        m = re.search(_regex_img_area,response.body)
        img_url = ''
        if m:
            content = m.group('content')
            _regex_image = r'zoomfile="(?P<img>.*?)"'
            mi = re.search(_regex_image,content)
            if mi:
                img_url = 'http://www.suppig.net/'+mi.group('img')
        _item['img_src'] = img_url

        if len(_item['torrents_reqs']) > 0:
            yield _item

    def _ban(self,content):
        for tag in self.BAN_TAG:
            if tag in content:
                return True
        return False

    def _unescape(self,content):
        return self.html_parser.unescape(content)

    def closed(self, reason):
        super(SuppigSpider, self).closed(reason)
