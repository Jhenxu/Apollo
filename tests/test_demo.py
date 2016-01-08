#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-08 11:48:24
#########################################################################

import unittest,urllib2,urllib

class TestTorrentDownload(unittest.TestCase):
    def setUp(self):
        print 'setup'

    def test_download(self):
        download_headers = {
            'Host':'www.bttiantang.com',
            'Connection':'keep-alive',
            'Pragma':'no-cache',
            'Cache-Control':'no-cache',
            'Origin':'http://www.bttiantang.com',
            'Upgrade-Insecure-Requests':1,
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
            'Content-Type':'application/x-www-form-urlencoded',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
        }
        body = {'action':'download'
            ,'uhash':'5526f8414c88d5798c421da9'
            ,'id':'3629'
            ,'imageField.y':'13'
            ,'imageField.x':'50'
            }
        url = 'http://www.bttiantang.com/download3.php'
        content = urllib.urlencode(body)
        req = urllib2.Request(url, content,headers=download_headers)
        response = urllib2.urlopen(req)
        result = response.read()
        print result
        self.assertTrue(200 == response.getcode())
        self.assertIsNotNone(result)

    def tearDown(self):
        print 'tearDown'

if __name__=='__main__':
    unittest.main()
