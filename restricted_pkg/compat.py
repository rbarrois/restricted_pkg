# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois.
# Distributed under the MIT License.

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    import urllib
    import configparser
else:
    import urllib2 
    import ConfigParser as configparser


def urlparse(*args, **kwargs):
    if PY3:
        return urllib.parse.urlparse(*args)
    else:
        return urllib2.urlparse.urlparse(*args)

def urlunparse(*args, **kwargs):
    if PY3:
        return urllib.parse.urlunparse(*args)
    else:
        return urllib2.urlparse.urlunparse(*args)
