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
import gtk
import sys, os
from lib import *
from libu import *
from libsetting import *

def __update_manager_setting():
    o = GConfCheckButton(_('Automatically check for update'), '/apps/update-notifier/auto_launch' )
    hbox = gtk.HBox(False, 10)
    hbox.pack_start( gtk.Label( _('Interval (in days) when to check for update:') ), False)
    e = GConfNumericEntry('/apps/update-notifier/regular_auto_launch_interval', 1, 30)
    hbox.pack_start(e, False)
    vbox = gtk.VBox(False, 0)
    vbox.pack_start(o, False)
    vbox.pack_start(hbox, False)
    return Setting(vbox, _('Ubuntu update manager setting'), ['update'])

def get():
    try:
        import gconf
    except: # python-gconf is missing 
        return []
    
    ret = []
    for f in [
            __update_manager_setting ,
             ]:
        try:
            ret.append(f())
        except:
            print_traceback()
    return ret
