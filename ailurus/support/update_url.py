#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Ailurus - make Linux easier to use
#
# Copyright (C) 2007-2010, Trusted Digital Technology Laboratory, Shanghai Jiao Tong University, China.
# Copyright (C) 2009-2010, Ailurus Developers Team
#
# Ailurus is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ailurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ailurus; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

from __future__ import with_statement

import sys,os,types
import os.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../')

from libapp import *
from common.apps import *

__doc__ = "automatically update URL to latest URL"

import HTMLParser

class UrlParser(HTMLParser.HTMLParser):
    def __init__(self,pattern=None):
        HTMLParser.HTMLParser.__init__(self)
        self.pattern = pattern
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name,value in attrs:
                if name == 'href' and str(value).startswith(self.pattern):
                    self.urls.append(str(value))
    def geturls(self):
        return self.urls

def get_app_objs_from_module(module):

    objs = []
    names = set()

    for name in dir(module):
        if name in names: continue
        if name[0] == '_' or name == 'I' or name == 'N':continue
        cls = getattr(comm.apps, name)
        
        if not isinstance(cls, types.ClassType) or not issubclass(cls, _ff_extension):continue

        try:
            cls_obj = cls()
            cls_obj.self_check()    
            
            objs.append(cls_obj)
            names.add(name)

        except:
            print "can't load class %s" %name
            print_traceback()

    return objs          

def get_latest_filename(old_filename, url):
    """get last modifed filename from given download HTTP/FTP URL"""
    import urllib2

    pattern = old_filename.split('-')[0]
    try:
        urlopen = urllib2.urlopen(url)
        rsp = urlopen.read().decode('UTF-8')
    except:
        print "url fetch failed, skip %s" %pattern
        return old_filename


    parser = UrlParser(pattern=pattern)
    parser.feed(rsp)

    # if there is only file entry, do nothing.
    if len(parser.urls) == 1:
        return old_filename

    latest_version = old_filename.split('-')[1]
    index = 0
    tag = 0
    for url in parser.urls:

        this_version = url.split('-')[1]
        if this_version > latest_version:
            latest_version = this_version
            tag = index

        index = index + 1        

    return parser.urls[tag]

def check_update(old, new):

    old_version = old.split('-')[1]
    new_version = new.split('-')[1]

    ret = False
    if new_version > old_version:
        ret = True

    return ret

if __name__ == "__main__":
    # testing codes here

    # enum all class instance in file common/apps.py
    comm = __import__('common')
    for obj in get_app_objs_from_module(comm.apps):
        print obj.name, "=>", obj.download_url
        print obj.R.url, obj.R.size, obj.R.hash, obj.R.filename 

        download_url = os.path.dirname(obj.R.url[0])
        latest_filename = get_latest_filename(obj.R.filename, download_url);

        old_filename = obj.R.filename          
        will_update = check_update(old_filename,latest_filename)
        if will_update:
            #obj.R.filename = latest_filename
            print "update %s from %s to %s" %(obj.name, old_filename, latest_filename)

        print ""


    print "Finished..."
    
    


