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
import gtk
from lib import *
from libu import *
from libsetting import Set

class SystemSettingPane(gtk.VBox):
    icon = D+'sora_icons/m_linux_setting.png'
    text = _('System\nSettings')

    def __left_pane(self):
        def icon(path):
            return get_pixbuf(path, 28, 28)
        
        existing_categories = []
        for i in self.setting_items:
            existing_categories += i.category_list()
        existing_categories = set(existing_categories)
        
        self.left_store = left_store = gtk.ListStore(gtk.gdk.Pixbuf, str, str) #pixbuf, text, category
        for iconpath, text, category in Set.array:
            if category in existing_categories:
                pixbuf = icon(iconpath)
                left_store.append([pixbuf, text, category])
                
        left_store_sort = gtk.TreeModelSort(left_store)
        left_store_sort.set_sort_column_id(1, gtk.SORT_ASCENDING)
        render_pixbuf = gtk.CellRendererPixbuf()
        render_text = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(render_pixbuf, False)
        column.add_attribute(render_pixbuf, 'pixbuf', 0)
        column.pack_start(render_text, False)
        column.add_attribute(render_text, 'text', 1)
        treeview = gtk.TreeView(left_store_sort)
        treeview.set_rules_hint(True)
        treeview.append_column(column)
        treeview.set_headers_visible(False)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.get_selection().connect('changed', self.__left_changed, treeview)
        treeview.get_selection().select_path('0')
        treeview_scrolled = gtk.ScrolledWindow()
        treeview_scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        treeview_scrolled.set_shadow_type(gtk.SHADOW_IN)
        treeview_scrolled.add(treeview)
        
        return treeview_scrolled
    
    def __left_changed(self, selection, treeview):
        model, iter = selection.get_selected()
        if iter == None: return
        
        for c in self.content_box.get_children():
            self.content_box.remove(c)
            
        display = model.get_value(iter, 2)
        for item in self.setting_items:
            if item.contain(display):
                self.content_box.pack_start(item.get_content(), False)
        self.content_box.show_all()
    
    def __right_pane(self):
        label = label_left_align( _('If you hover mouse pointer above any item, you can read Linux setting skills :)') )
        label.set_border_width(5)
        
        self.content_box = content_box = gtk.VBox(False, 0)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(content_box)
        
        bigbox = gtk.VBox(False, 0)
        bigbox.pack_start(label, False)
        bigbox.pack_start(scroll)
        
        return bigbox
    
    def __init__(self, main_view, setting_items):
        for i in setting_items:
            assert issubclass(i, Set)
        
        self.setting_items = setting_items
        
        gtk.VBox.__init__(self, False)
        right = self.__right_pane()
        left = self.__left_pane()
        paned = gtk.HPaned()
        paned.pack1(left, False, False)
        paned.pack2(right, True, True)
        self.pack_start(paned)
