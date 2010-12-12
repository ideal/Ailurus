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
import gtk, sys, os
from lib import *
from libu import *

missing_files = [] # used only in get_information_pixbuf. do not continuously display error messages.

def get_information_pixbuf(path, width, height):
    if not os.path.exists(path):
        global missing_files
        if path not in missing_files:
            print path, 'is missing'
            missing_files.append(path)
        path = D+'sora_icons/default_information_icon.png'
    return get_pixbuf(path, width, height)

class InfoPane(gtk.VBox):
    icon = D+'sora_icons/m_hardware.png'
    text = _('Information')

    def print_all_information(self):
        import StringIO
        f = StringIO.StringIO()
        
        root = self.treestore.get_iter_first()
        while root:
            value1 = self.treestore.get_value(root, 1)
            print >>f, value1
            
            child = self.treestore.iter_children(root)
            while child:
                value1 = self.treestore.get_value(child, 1)
                value2 = self.treestore.get_value(child, 2)
                print >>f, '  ', value1
                print >>f, '    ', value2
                child = self.treestore.iter_next(child)
                
            root = self.treestore.iter_next(root)

        show_text_window(_('Information'), f.getvalue())

    def __init__(self, main_view, infos):
        assert isinstance(infos, tuple) and len(infos) == 2
        assert isinstance(infos[0], list)
        assert isinstance(infos[1], list)
        hardware_functions, os_functions = infos
        self.hardware_functions = hardware_functions
        self.os_functions = os_functions
        for func in hardware_functions:
            func.result = func()
        for func in os_functions:
            func.result = func()
        
        self.hardware_subtree_text = _('Hardware Information')
        self.hardware_subtree_icon = get_pixbuf(D + 'sora_icons/m_hardware.png', 24, 24)
        self.os_subtree_text = _('Linux Information')
        self.os_subtree_icon = get_pixbuf(D+'sora_icons/m_linux.png', 24, 24)
        
        gtk.VBox.__init__(self, False, 10)
        
        button = image_stock_button(gtk.STOCK_PRINT, _('Print all information'))
        button.connect('clicked', lambda w: self.print_all_information())
        align_button = gtk.Alignment(0, 0.5)
        align_button.add(button)
        
        self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str, str)
        self.treeview = treeview = gtk.TreeView(self.treestore)
        column = gtk.TreeViewColumn()
        treeview.append_column(column)
        treeview.set_headers_visible(False)
        pixbuf_render = gtk.CellRendererPixbuf()
        text_render = gtk.CellRendererText()
        value_render = gtk.CellRendererText()
        column.pack_start(pixbuf_render, False)
        column.add_attribute(pixbuf_render, 'pixbuf', 0)
        column.pack_start(text_render, False)
        column.add_attribute(text_render, 'text', 1)
        column.pack_start(value_render, False)
        column.add_attribute(value_render, 'text', 2)
        
        scrollwindow = gtk.ScrolledWindow ()
        scrollwindow.add (treeview)
        scrollwindow.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type (gtk.SHADOW_IN)
        
        self.pack_start(scrollwindow)
        self.pack_start(align_button, False)
        
        self.refresh()

        import gobject
        gobject.timeout_add(5000, self.refresh)
    
    def refresh(self):
        for func in self.hardware_functions:
            if hasattr(func, 'please_refresh_me'):
                func.result = func()
                if func.result is None:
                    func.result = []

        for func in self.os_functions:
            if hasattr(func, 'please_refresh_me'):
                func.result = func()
                if func.result is None:
                    func.result = []

        self.treestore.clear()
        
        subtree_root = self.treestore.append(None, [self.hardware_subtree_icon, self.hardware_subtree_text, None])
        for func in self.hardware_functions:
            for row in func.result:
                pixbuf = get_information_pixbuf(row[2], 24, 24)
                self.treestore.append(subtree_root, [pixbuf, row[0], row[1]])
                
        subtree_root = self.treestore.append(None, [self.os_subtree_icon, self.os_subtree_text, None])
        for func in self.os_functions:
            for row in func.result:
                pixbuf = get_information_pixbuf(row[2], 24, 24)
                self.treestore.append(subtree_root, [pixbuf, row[0], row[1]])

        self.treeview.expand_all()

        return True
