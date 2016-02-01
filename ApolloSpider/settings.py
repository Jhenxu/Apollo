# -*- coding: utf-8 -*-

# Scrapy settings for Apollo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
from ApolloCommon import config

BOT_NAME = 'ApolloSpider'

SPIDER_MODULES = ['ApolloSpider.spiders']
NEWSPIDER_MODULE = 'ApolloSpider.spiders'

LOG_LEVEL = 'INFO'
LOG_ENCODING = 'utf-8'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Apollo (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
        'ApolloSpider.pipelines.ApolloImagePipline':99,
        'ApolloSpider.pipelines.TorrentPipeline.TorrentPipeline':101,
        'ApolloSpider.pipelines.MongodbPipeline':102,
        }

DOWNLOADER_MIDDLEWARES = {
    'ApolloSpider.middlewares.TestMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
    # 'ApolloSpider.middlewares.randomproxy.RandomProxy': 100,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
}

EXTENSIONS = {
        }

IMAGES_THUMBS = {
    'thumb': (200, 200),
    'mobile': (320, 320),
}

#DOWNLOAD_DELAY = 0.5
DOWNLOAD_TIMEOUT = 20

IMAGES_STORE = config.get('IMAGES_STORE')
IMAGES_EXPIRES = 180        #根据lastmodify
TORRENTS_STORE = config.get('TORRENTS_STORE')
TORRENT_EXPIRES = 180       #根据lastmodify
FILE_EXPIRES = -1           #根据文件修改日期IMAGES TORRENT 0:过期 -1:不过期
APOLLO_ITEM_DEEP_SPIDER = 7      #深度爬取时间间隔（已经存在的item再次深度爬取）
APOLLO_FULL_SPIDER = 30     #0 总是完全 -1 第一次完全爬取后以后一直不完全爬取 >0 完全爬取间隔天数

# # RandomProxy Retry many times since proxies often fail
# RETRY_TIMES = 10
# # RandomProxy Retry on most error codes since proxies fail for different reasons
# RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]
#
# # RandomProxy
# # Proxy list containing entries like
# # http://host1:port
# # http://username:password@host2:port
# # http://host3:port
# # ...
# PROXY_LIST = '/path/to/proxy/list.txt'
