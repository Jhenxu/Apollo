# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from ApolloWeirdSpider.items import FortuneItem
from common.mongodb import MongoAgentFactory
from scrapy import Request,log

class ApolloweirdspiderPipeline(object):
    def __init__(self):
        self.db = MongoAgentFactory.getNoWarpDB()

    def process_item(self, item, spider):
        if isinstance(item,FortuneItem):
            dbItem = self.db.find_one({'key':item.getKey()})
            if dbItem == None:
                result = self.db.insert(item.toDBItem())
                log.msg('插入新条目:'+str(item['key'].encode('utf-8')),level=log.INFO)
            else:
                log.msg('已存在条目:'+item.getKey(),level=log.INFO)
        return item
