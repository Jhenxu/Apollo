#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2015-12-05 17:15:08
#########################################################################
import os,time

def isFileExpire(f,expire=0):
    if expire == 0:
        return True

    file_last_modify = 0.0

    try:
        if isinstance(f,str):
            file_last_modify = os.path.getmtime(f)
        elif isinstance(f,file):
            file_last_modify = os.path.getmtime(f.name)
    except OSError:
        return True

    if expire < 0:
        return False

    expire_ts = expire*24*60*60
    if (time.time()-file_last_modify) > expire_ts:
        return True
    else:
        return False
