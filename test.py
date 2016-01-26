#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 22:54:47
#########################################################################
from ApolloCommon.torrentparse import TorrentParser
import glob,os
from ApolloCommon.mongodb import MongoAgentFactory as Agent

# test_dir = os.path.join(os.getcwd(), './static/torrents2/')
# for f in os.listdir(test_dir):
#     file_path = os.path.join(test_dir,f)
#     tp = TorrentParser(file_path)
#     print file_path
#     print tp.is_torrent()
#     if tp.is_torrent():
#         print tp.get_tracker_url(), tp.get_creation_date(), tp.get_client_name(), tp.get_files_details()
#     print '*' * 80


db = Agent.getDB()
print '##########'
print db.find_one({'status':10})

#print Agent.getNoWarpDB().find_one({'years':2016})
