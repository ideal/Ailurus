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

from lib import *

class WindowPos:
    @classmethod
    def save(cls, window, name):
        x,y = window.get_position()
        width, height = window.get_size()
        Config.set_int('window_%s_x'%name, x)
        Config.set_int('window_%s_y'%name, y)
        Config.set_int('window_%s_width'%name, width)
        Config.set_int('window_%s_height'%name, height)
    @classmethod
    def load(cls, window, name, set_default=True):
        try:
            x = Config.get_int('window_%s_x'%name)
            y = Config.get_int('window_%s_y'%name)
            window.move(x, y)
        except:
            if set_default:
                import gtk
                window.set_position(gtk.WIN_POS_CENTER)
                
        try:
            width = Config.get_int('window_%s_width'%name)
            height = Config.get_int('window_%s_height'%name)
            window.resize(width, height)
        except:
            if set_default:
                window.resize(600,400)
