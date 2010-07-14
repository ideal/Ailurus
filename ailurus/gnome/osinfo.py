#-*- coding: utf-8 -*-
#
# Ailurus - make Linux easier to use
#
# Copyright (C) 2009-2010, Ailurus developers and Ailurus contributors
# Copyright (C) 2007-2010, Trusted Digital Technology Laboratory, Shanghai Jiao Tong University, China.
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
import sys, os
from lib import *

def __gnome():
    import os, re
    ret = []
    
    try:
        with open('/usr/share/gnome-about/gnome-version.xml') as f:
            for line in f:
                if 'platform' in line:
                    platform = re.search('<platform>(.+)</platform>', line).group(1)
                elif 'minor' in line:
                    minor = re.search('<minor>(.+)</minor>', line).group(1)
                elif 'micro' in line:
                    micro = re.search('<micro>(.+)</micro>', line).group(1)
                    break
        string = "%s.%s.%s" % (platform, minor, micro)
        ret.append( row(_('GNOME version:'), string, D+'umut_icons/i_gnome.png' ) )
    except:
        print_traceback()
        
    try: ret.append( row(_('GNOME locale:'), os.environ['LANG'], D+'sora_icons/i_locale.png' ) )
    except: print_traceback()

    return ret

def get():
    return [__gnome]
