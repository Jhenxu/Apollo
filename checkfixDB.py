#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: fix.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-06 01:39:57
#########################################################################
import re
from pymongo.connection import MongoClient

client = MongoClient('localhost',27017)
db = client['apollo_db']['apollo_item']

# for item in db.find():
# 	b = item['years']
#
# 	if not isinstance(b,int):
# 		try:
# 			if not None == b and not '' == b.strip():
# 				item['years'] = int(b[0])
# 			else:
# 				item['years'] = 0
# 		except ValueError:
# 			item['years'] = 0
#
# 	b = item['douban_score']
#
# 	if not isinstance(b,float):
# 		if not b == None and not '' == b.strip():
# 			item['douban_score'] = float(b)
# 		else:
# 			item['douban_score'] = 0.0
#
# 	if not isinstance(item['tags'],list):
# 		item['tags'] = item['tags'].split(',')
# 	if not isinstance(item['area'],list):
# 		item['area'] = item['area'].split(',')
# 	if not isinstance(item['director'],list):
# 		item['director'] = item['director'].split(',')
# 	if not isinstance(item['alias'],list):
# 		item['alias'] = item['alias'].split(',')
# 	if not isinstance(item['starring'],list):
# 		item['starring'] = item['starring'].split(',')
# 	if not isinstance(item['screenwriter'],list):
# 		item['screenwriter'] = item['screenwriter'].split(',')
#
# 	_id = item['_id']
# 	del item['_id']
# 	db.update({'_id':_id},{'$set':item})

def check():
	for item in db.find():
		if isinstance(item['years'],int) and isinstance(item['douban_score'],float) and isinstance(item['tags'],list)\
			and isinstance(item['area'],list) and isinstance(item['director'],list) and isinstance(item['alias'],list)\
			and isinstance(item['starring'],list) and isinstance(item['screenwriter'],list):
			pass
		else:
			print 'failed'
			print 'years:'+str(isinstance(item['years'],int))
			break
	print 'success'

check()
