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

import gtk, pango

class SplashWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_decorated(False)
        
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(15)
        color = gtk.gdk.color_parse('#202020')
        self.modify_bg(gtk.STATE_NORMAL, color)
        
        from lib import D
        logo = gtk.Image()
        logo.set_from_file(D+'suyun_icons/logo_with_reflection.png')
        
        title = gtk.Image()
        title.set_from_file(D+'velly_icons/ailurus_for_splash.png')
        
        comment = gtk.Label()
        comment.set_markup(
            _('<span color="grey">'
              '<span color="#00A0E9">Help</span> <span color="grey">you install some nice applications.\n</span>'
              '<span color="#00A0E9">Help</span> you do tedious settings.\n'
              '<span color="#00A0E9">Tell</span> you some Linux skills.'
              '</span>') )
        comment.modify_font(pango.FontDescription('Purisa 12'))
       
        titlevbox = gtk.VBox(False, 0)
        titlevbox.pack_start(title, False)
        titlevbox.pack_start(comment, False)

        box = gtk.HBox()
        box.pack_start(titlevbox, False)
        box.pack_start(logo, True)

        self.add(box)
