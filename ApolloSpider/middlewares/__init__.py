#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-15 15:18:09
#########################################################################

import re,time
import random
import base64
from scrapy import log

class TestMiddleware(object):

    def process_request(self, request, spider):
        # request.meta['proxy'] = 'http://127.0.0.1:8888'
        #print '### TestMiddleware process_request '+request.url
        if not 'proxy' in request.meta and 'apollo_random_proxy' in request.meta:
            if request.meta['apollo_random_proxy']:
                # request.meta['proxy'] = 'http://24.173.40.24:8080'
                print '### setproxy ' + request.url
        # Don't overwrite with a random one (server-side state for IP)
        # if 'proxy' in request.meta:
        #     return
        #
        # proxy_address = random.choice(self.proxies.keys())
        # proxy_user_pass = self.proxies[proxy_address]
        #
        # request.meta['proxy'] = proxy_address
        # if proxy_user_pass:
        #     basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
        #     request.headers['Proxy-Authorization'] = basic_auth

    def process_exception(self, request, exception, spider):
        print '### TestMiddleware process_exception'+str(exception)
        # proxy = request.meta['proxy']
        # log.msg('Removing failed proxy <%s>, %d proxies left' % (
        #             proxy, len(self.proxies)))
        # try:
        #     del self.proxies[proxy]
        # except ValueError:
        #     pass
