#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-05 17:15:08
#########################################################################
import os,time

def isFileExpire(file,expire=0):
    if expire == 0:
        return True

    file_last_modify = 0.0

    try:
        if isinstance(file,str):
            file_last_modify = os.path.getmtime(file)
        elif isinstance(file,file):
            file_last_modify = os.path.getmtime(file.name)
    except OSError:
        return True

    if expire < 0:
        return False

    expire_ts = expire*24*60*60
    if (time.time()-file_last_modify) > expire_ts:
        return True
    else:
        return False
