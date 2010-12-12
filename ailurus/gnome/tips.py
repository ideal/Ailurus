#coding: utf-8
#
# Ailurus - a simple application installer and GNOME tweaker
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

def get():
    return [
_('''$HOME/.thumbnails/ directory is a cache dir GNOME makes when you browse through your folders in nautilus. 
It contains thumbnail pictures of picture files you've previously looked at.

You can get its total size by 
du -bs $HOME/.thumbnails/

You can delete the files in the .thumbnails directory that haven't been accessed for seven days, to free disk space.
find $HOME/.thumbnails/ -type f -atime +7 -exec rm {} \;
'''),

_("""Capture screen after 10 seconds
gnome-screenshot -d 10
Capture current window after 10 seconds
gnome-screenshot -wd 10
"""),

_('''Start GConf editor:
Press Alt+F2, type 'gconf-editor'.'''),
]
    