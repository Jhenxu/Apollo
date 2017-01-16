# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy,hashlib
from scrapy.item import Item,Field

class FortuneItem(Item):

    def __init__(self,star,date):
        scrapy.Item.__init__(self)
        self['star'] = star
        self['date'] = date
        self['fortunePart'] = {}
        self['secPart'] = {}
        self['key'] = ''

    star = Field()
    date = Field()
    fortunePart = Field()
    secPart = Field()
    key = Field()

    def getKey(self):
        if None == self['key'] or '' == self['key']:
            code = '%s_%s'%(self['star'],self['date'])
            self['key'] = hashlib.sha1(code).hexdigest()
            return self['key']
        else:
            return self['key']

    def toDBItem(self):
        result = {}
        result['key'] = self.getKey()
        result['star'] = self.get('star','')
        result['date'] = self['date']
        result['fortunePart'] = self['fortunePart']
        result['secPart'] = self['secPart']
        return result
