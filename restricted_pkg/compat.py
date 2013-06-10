# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois.
# Distributed under the MIT License.

import sys

if sys.version_info[0] >= 3:
    from urllib.parse import urlparse
    import configparser
else:
    from urllib2 import urlparse
    import ConfigParser as configparser


