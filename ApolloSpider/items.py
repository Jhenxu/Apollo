# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field
import scrapy,time,hashlib

class ApolloItem(Item):
    def __init__(self,platform):
        scrapy.Item.__init__(self)
        self['platform'] = platform
        self['torrents'] = []
        self['torrents_reqs'] = []
        self['meta'] = {}
        self['years'] = 0

    platform        = Field()   #平台标记 str
    title           = Field()   #名称     str
    alias           = Field()   #又名     list
    tags            = Field()   #标签     list
    area            = Field()   #地区       list
    years           = Field()   #年份     int
    director        = Field()   #导演       list
    screenwriter    = Field()   #编剧       list
    starring        = Field()   #主演      list
    imdb            = Field()   #imdb      str
    douban_id       = Field()   #豆瓣id         str
    img             = Field()   #图片本地路径    str
    torrents        = Field()   #种子信息       []

    img_ore         = Field()   #图片源地址
    torrents_reqs   = Field()   #种子地址request
    meta            = Field()   #临时数据dict

    def binfo(self):
        result = {
                'platform':self.get('platform',''),
                'title':self.get('title',''),
                'alias':self.get('alias',[]),
                'tags':self.get('tags',[]),
                'area':self.get('area',[]),
                'director':self.get('director',[]),
                'screenwriter':self.get('screenwriter',[]),
                'starring':self.get('starring',[]),
                'imdb':self.get('imdb',''),
                'douban_id':str(self.get('douban_id','')),
                'stars':self.get('stars',0),
                'img':self.get('img',''),
                }
        return result


    def toDBItem(self):
        result = self.binfo()
        result['key'] = self.getKey()
        result['years'] = self['years']
        result['torrents'] = self.get('torrents',[])
        result['torrents_size'] = len(self.get('torrents',[]))
        result['timestamp'] = time.time()
        #ins_ts 插入时更新
        return result

    def getKey(self):
        code = '%s_%s'%(str(self['title'].encode('utf-8')),self['years'])
        return hashlib.sha1(str(code)).hexdigest()

    def __setitem__(self, key, value):
        if key in self.fields:
            if isinstance(value,str):
                self._values[key] = value.decode('utf-8')
            elif isinstance(value,list):
                nValue = []
                for i in value:
                    if isinstance(i,str):
                        nValue.append(i.decode('utf-8'))
                self._values[key] = nValue
            elif isinstance(value,dict):
                nValue = {}
                for k,v in value.items():
                    if isinstance(k,str):
                        k = k.decode('utf-8')
                    if isinstance(v,str):
                        v = v.decode('utf-8')
                    nValue[k] = v
                self._values[key] = nValue
            elif isinstance(value,int):
                self._values[key] = value
            elif isinstance(value,float):
                self._values[key] = value
            elif isinstance(value,unicode):
                self._values[key] = value
            else:
                raise TypeError
        else:
            raise KeyError("%s does not support field: %s" %
                (self.__class__.__name__, key))

class DoubanItem(Item):

    def __init__(self,platform):
        super(DoubanItem,self).__init__()
        self['platform'] = platform

    platform        = Field()   #平台标记 str
    key             = Field()   #douban id
    summary         = Field()   #简介
    rating_score    = Field()   #豆瓣评分
    ratings_count   = Field()   #评分计数
    year            = Field()   #年份
    mobile_url      = Field()   #url
    content         = Field()   #response.body
    img             = Field()   #download img path

    img_ore         = Field()   #海报地址
    apollo_item     = Field()   #ApolloItem mogonid

    def toDBItem(self):
        result = {
                'platform':self.get('platform',''),
                'key':self.get('key',''),
                'summary':self.get('summary',''),
                'rating_score':self.get('rating_score',0),
                'ratings_count':self.get('ratings_count',0),
                'year':self.get('year',0),
                'mobile_url':self.get('mobile_url',''),
                'content':self.get('content',''),
                'img':self.get('img',''),
                'update':time.time(),
                }
        return result
