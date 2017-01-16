#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name:
# Author: Jhenxu
# mail: jhenxu@gmail.com
# Created Time: 2014-01-31 12:49:17
#########################################################################

# 使用装饰器(decorator),
# 这是一种更pythonic,更elegant的方法,
# 单例类本身根本不知道自己是单例的,因为他本身(自己的代码)并不是单例的
# 使用此装饰器以后无法直接使用类方法和静态方法(Cls.classmethod,Cls.staticmethod)
def singleton(cls, *args, **kw):
        instances = {}
        def _singleton():
            if cls not in instances:
                instances[cls] = cls(*args, **kw)
            return instances[cls]
        return _singleton
