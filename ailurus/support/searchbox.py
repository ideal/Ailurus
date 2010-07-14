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

import gtk
import gobject

class SearchBoxForApp(gtk.HBox):
    __gsignals__ = {'changed':( gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                                (gobject.TYPE_STRING, gobject.TYPE_STRING)  ) }
    
    def __init__(self):
        gtk.HBox.__init__(self, False, 3)
        label = gtk.Label( _('Search items:') )
        self.__entry = entry = gtk.Entry()
        entry.connect('changed', self.__entry_changed)
        entry.connect('key_press_event', self.__entry_key_press)
        button_clear=gtk.Button()
        button_clear.set_relief(gtk.RELIEF_NONE)
        button_clear.add(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON))
        button_clear.connect('clicked', self.__clear_entry)
        self.__combo = option = gtk.combo_box_new_text()
        option.append_text( _('In names only.' ) )
        option.append_text( _('In names & details.' ) )
        option.set_active(1)
        option.connect('changed', self.__option_changed)
        self.pack_start(option, False, False)
#        self.pack_start(label, False, False)
        self.pack_start(entry)
        self.pack_start(button_clear,False,False)
    def __text(self):
        return self.__entry.get_text()
    def __option(self):
        return [ 'name','both' ] [ self.__combo.get_active() ]
    def __option_changed(self, widget):
        self.emit('changed', self.__text(), self.__option())
    def __entry_changed(self, widget):
        self.emit('changed', self.__text(), self.__option())
    def __entry_key_press(self, widget, event):
        if event.keyval==gtk.keysyms.Escape:
            self.__entry.set_text('')
        return False
    def __clear_entry(self, widget):
        self.__entry.set_text('')

class SearchBox(gtk.HBox):
    def __init__(self, func):
        self.func = func
        gtk.HBox.__init__(self, False, 5)
        label = gtk.Label( _('Search') )
        self.__entry = entry = gtk.Entry()
        entry.connect("changed", self.__entry_changed)
        entry.connect("key_press_event",self.__entry_key_press)
        stock_clear=gtk.Image()
        stock_clear.set_from_stock(gtk.STOCK_CLEAR,gtk.ICON_LOOKUP_USE_BUILTIN)
        button_clear=gtk.Button()
        button_clear.set_relief(gtk.RELIEF_NONE)
        button_clear.add(stock_clear)
        button_clear.connect('clicked',self.__clear_entry)
        self.pack_start(label, False, False)
        self.pack_start(entry)
        self.pack_start(button_clear, False, False)
    def __text(self):
        return self.__entry.get_text()
    def __entry_changed(self, widget):
        self.func(self.__text())
    def __entry_key_press(self, widget, event):
        if event.keyval==gtk.keysyms.Escape:
            self.__entry.set_text('')
        return False
    def __clear_entry(self, widget):
        self.__entry.set_text('')
