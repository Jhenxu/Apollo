#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2016-01-11 22:54:47
#########################################################################
from ApolloCards.managers import AppCardsManager

cm = AppCardsManager()
#print cm.newest()
#print cm.top_movie()
print cm.action_movie()
