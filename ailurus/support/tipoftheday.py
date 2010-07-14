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
from libu import *

tips = None

import gtk

class TipOfTheDay(gtk.Window):
    def __change_content (self, content, text):
        content.get_buffer().set_text(text)
    
    def __random ( self, content ):
        i = self.lasttip
        while i == self.lasttip:
            import random
            i = random.randint ( 0, len(self.tips)-1 )
        self.lasttip = i
        self.__change_content(content, self.tips[i])
    
    def __next_tip (self, widget, content):
        self.lasttip += 1
        if self.lasttip == len(self.tips):
            self.lasttip = 0
        self.__change_content(content, self.tips[self.lasttip])
    
    def __previous_tip (self, widget, content):
        if self.lasttip == 0:
            self.lasttip = len(self.tips)
        self.lasttip -= 1
        self.__change_content(content, self.tips[self.lasttip])
    
    def __show_all_tips(self, widget):
        show_text_window(_('All Linux skills'), '\n\n'.join(tips))

    def __init__(self):
        import gtk
        from support.releasenotesviewer import ReleaseNotesViewer
        gtk.Window.__init__(self)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title(_('Tip of the Day'))
        self.set_border_width(10)
        
        title = gtk.Label ()
        title.set_markup ( _('<span size="x-large"><b>Did you know ?</b></span>') )
        title.set_alignment(0.5, 0.5)
        titlebox = gtk.HBox (False, 10)
        titlebox.pack_start (gtk.image_new_from_stock ( gtk.STOCK_DIALOG_INFO, 
                                                        gtk.ICON_SIZE_DIALOG ),
                             False, False, 0)
        titlebox.pack_start (title)

        content = ReleaseNotesViewer()
        gray_bg(content)
        content.set_cursor_visible(False)
        content.set_wrap_mode(gtk.WRAP_WORD)
        
        scroll_content = gtk.ScrolledWindow()
        scroll_content.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_content.add(content)
        scroll_content.set_size_request(-1, 200)

        close_button =  stock_image_only_button(gtk.STOCK_CLOSE )
        def close_me(w):
            self.destroy()
        close_button.connect( 'clicked', close_me )

        next_tip = stock_image_only_button(gtk.STOCK_GO_FORWARD)
        next_tip.connect ( 'clicked', self.__next_tip, content )
        next_tip.grab_focus()
        
        previous_tip = stock_image_only_button(gtk.STOCK_GO_BACK)
        previous_tip.connect ( 'clicked', self.__previous_tip, content )
        
        submit_skills = image_stock_button(gtk.STOCK_GO_UP, _('Submit Linux Skills'))
        submit_skills.connect('clicked', report_bug)
        
        show_all_tips = image_stock_button(gtk.STOCK_INDEX, _('Show all tips'))
        show_all_tips.connect('clicked', self.__show_all_tips)
        
        hbox = gtk.HBox(False, 10)
        hbox.pack_end(close_button, False, False)
        hbox.pack_end(next_tip, False, False)
        hbox.pack_end(previous_tip, False, False)
        hbox.pack_end(submit_skills, False, False)
        hbox.pack_end(show_all_tips, False, False)

        box = gtk.VBox ( False, 0 )
        box.pack_start ( titlebox, False )
        box.pack_start ( scroll_content, False )
        box.pack_start ( hbox, False )
        box.show_all()

        self.add(box)
        global tips
        if tips == None:
            import loader
            tips = loader.load_tips() 
        self.tips = tips
        assert isinstance(self.tips, list)
        for e in self.tips:
            assert isinstance(e, (str,unicode) )
        self.lasttip = None
        self.__random ( content ) # show the first tip
        self.show_all()