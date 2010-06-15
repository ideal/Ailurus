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
import sys, os
from lib import *

def __ubuntu():
    try: 
        with open('/etc/lsb-release') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('DISTRIB_RELEASE='):
                value = line.split('=')[1].strip()
        return [row(_('Ubuntu version:'), value, D+'other_icons/ubuntu.png' )]
    except: print_traceback()

def __ubuntu_derivative():
    try:
        import platform
        name, version = platform.dist()[0:2]
        return [row(_('%s version:') % name, version, D+'umut_icons/tux.png' )]
    except: print_traceback()

def get():
    if UBUNTU:
        return [__ubuntu]
    elif UBUNTU_DERIV: # Ubuntu derivative
        return [__ubuntu_derivative]
    else:
        raise Exception # This must be a bug.