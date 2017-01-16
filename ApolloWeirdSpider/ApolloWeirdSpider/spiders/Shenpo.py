#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2017-01-13 10:37:57
#########################################################################
import re,time
from scrapy.spider import BaseSpider
from scrapy.http import Request
from ApolloWeirdSpider.items import FortuneItem

class ShenpoSpider(BaseSpider):
    name = "shenpo"
    start_urls = [
        'http://www.meiguoshenpo.com/meiri/',
        'http://www.meiguoshenpo.com/meiri/p2.html',
        'http://www.meiguoshenpo.com/meiri/p3.html',
        'http://www.meiguoshenpo.com/meiri/p4.html',
        'http://www.meiguoshenpo.com/meiri/p5.html',
    ]

    def parse(self, response):
        _regex_li = r'<div class="list_item">\n<h4><a href="(?P<link>.*?)">(?P<name>.*?)<\/a><\/h4>'

        for item in re.findall(_regex_li,response.body):
            req = Request(url=item[0],callback=self.parseItem,dont_filter=True)
            req.meta['title'] = item[1]
            yield req
        # req = Request(url='http://www.meiguoshenpo.com/meiri/d188024.html',callback=self.parseItem,dont_filter=True)
        # req.meta['title'] = '白羊座今日运势2017年1月13日'
        # yield req

    def parseItem(self,response):
        _regex_part = r'<p><strong>(.*?)<\/strong><br\/>(.*?)<\/p>'
        _regex_part_lucy = r'<meta name="description" content="(?P<content>[\s\S]*?)" \/>'
        match = re.search(_regex_part_lucy,response.body)
        fortuneItem = None
        if match:
            title = response.meta['title']
            _regex_date = r'\d{4}年\d{1,2}月\d{1,2}日'
            m = re.search(_regex_date,title)
            if m:
                date = time.strftime('%Y%m%d',time.strptime(m.group(),'%Y年%m月%d日'))
                fortuneItem = FortuneItem(title[:9],date)

            if not None == fortuneItem:
                fortune = match.group('content')
                for item in fortune.split('\n'):
                    sp = item.split('：')
                    name = sp[0]
                    stars = item.count('★')
                    fortuneItem['fortunePart'][name] = stars

                for item in re.findall(_regex_part,response.body):
                    if '<br/>' in item[1]:#<p><strong>今日开运</strong><br/>幸运数字：3<br/>幸运颜色：科幻银<br/>贵人星座：白羊座<br/>开运方位：西南方向<br/>今日吉时：pm:5:00--6:00</p>
                        fortuneItem['secPart'][item[0]] = {}
                        r = item[1].split('<br/>')
                        for i in r:
                            if '：' in i:#幸运数字：3 今日吉时：pm:5:00--6:00
                                r1 = i.split('：')
                                fortuneItem['secPart'][item[0]][r1[0]] = r1[1]
                    else:#<p><strong>运势短评</strong><br/>小心言语过激惹来纠纷。</p>
                        fortuneItem['secPart'][item[0]] = item[1]
            yield fortuneItem
