# -*- coding: utf-8 -*-

# Scrapy settings for ApolloWeirdSpider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ApolloWeirdSpider'

SPIDER_MODULES = ['ApolloWeirdSpider.spiders']
NEWSPIDER_MODULE = 'ApolloWeirdSpider.spiders'

LOG_LEVEL = 'INFO'
LOG_ENCODING = 'utf-8'

USER_AGENT =  'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'

ITEM_PIPELINES = {
        'ApolloWeirdSpider.pipelines.ApolloweirdspiderPipeline':99,
        }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ApolloWeirdSpider (+http://www.yourdomain.com)'
