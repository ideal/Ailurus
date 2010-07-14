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
import gobject
import sys
import os
from lib import *
from libu import *

class ReposConfigPane(gtk.VBox):
    icon = D+'sora_icons/m_repository_configure.png'
    text = _('Repository\nConfigure')
    
    def __init__(self, main_view):
        gtk.VBox.__init__(self, False)
        self.treestore = treestore = gtk.TreeStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT)
        self.treeview = treeview = gtk.TreeView(self.treestore)
        
        toggle_render = gtk.CellRendererToggle()
        toggle_render.set_property('activatable', True)
        toggle_render.connect('toggled',self.__toggled, treestore)
        toggle_column = gtk.TreeViewColumn()
        toggle_column.pack_start(toggle_render, False)
        toggle_column.set_cell_data_func(toggle_render, self.__toggle_cell_func)
        
        text_render = gtk.CellRendererText()
        text_render.connect('edited', self.__edited)
        text_column = gtk.TreeViewColumn()
        text_column.pack_start(text_render, False)
        text_column.set_cell_data_func(text_render, self.__text_cell_func)
        
        treeview.append_column(toggle_column)
        treeview.append_column(text_column)
        treeview.set_rules_hint(True)
        self.__refresh_tree()
        
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.add(treeview)
        scrollwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_IN)
        self.addArea = addArea = AddReposArea()
        self.add_btn = add_btn = image_stock_button(gtk.STOCK_ADD, _('Add'))
        add_btn.connect('clicked', self.__add_repos)
        buttom_box = gtk.HBox(False, 0)
        buttom_box.set_border_width(2)
        buttom_box.pack_start(addArea, True)
        buttom_box.pack_end(add_btn, False)
        
        self.treeview.expand_all()
        
        self.pack_start(scrollwindow)
        self.pack_start(buttom_box, False)
    
    def __toggle_cell_func(self, column, cell, model, iter):
        b = model.get_value(iter, 0)
        cell.set_property('active', b)
#        cell.set_property('inconsistent', True)
    
    def __text_cell_func(self, column, cell, model, iter):
        text = model.get_value(iter, 1)
        b = model.get_value(iter, 0)
        is_path = model.get_value(iter, 3)
        if is_path == -1:
            cell.set_property('markup', '<b><big>%s</big></b>' % text)
        elif not b:
            cell.set_property('markup', '<span color="gray">%s</span>' % text)
        else:
            cell.set_property('markup', self.__color_text(text))
        cell.set_property('editable', True)
    
    def __color_text(self, text):
        words = text.split()
        
        if len(words) < 4:
            return text
        
        def check_deb(word):
            deb_heads = ['deb', 'deb-src']
            for deb_head in deb_heads:
                if word.startswith(deb_head):
                    return True
            return False
        
        def check_url(word):
            url_heads = ['http://', 'ftp://', 'https://', 'rstp://']
            for url_head in url_heads:
                if word.startswith(url_head):
                    return True
            return False
        
        if not check_deb(words[0]):
            return text
        if not check_url(words[1]):
            return text
        words[0] = '<span color="#6900B2">%s</span>' % words[0]
        words[1] = '<b><span color="red">%s</span></b>' % words[1]
        words[2] = '<span color="#007243">%s</span>' % words[2]
        for i in range(3, len(words)):
            words[i] = '<span color="blue">%s</span>' % words[i]
        return ' '.join(words)
    
    def __get_repos_lines(self):
        import glob
        
        lines = {}
        with open('/etc/apt/sources.list', 'r') as f:
            lines['/etc/apt/sources.list'] = f.readlines()
        for path in glob.glob('/etc/apt/sources.list.d/*'):
            with open(path, 'r') as f:
                lines[path] = f.readlines()
        return lines
    
    def __refresh_tree(self):
        self.__souces_list = lines = self.__get_repos_lines()
        self.treestore.clear()
        for path in lines.keys():
            i = 0
            parent = self.treestore.append(None, [True, path, path, -1])
            for line in lines[path]:
                line = line.strip()
                if len(line) >= 2:
                    if line[0] == '#' and line[1:].strip().startswith('deb'):
                        self.treestore.append(parent, [False, line[1:], path, i])
                    elif line.startswith('deb'):
                        self.treestore.append(parent, [True, line, path, i])
                i += 1
            self.__set_parent_toggle(parent)
        
    def __apply(self):
        for path in self.__souces_list.keys():
            with TempOwn(path) as o:
                with open(path, 'w') as f:
                    for line in self.__souces_list[path]:
                        if line:
                            f.write(line)
    
    def __toggled(self, cellrenderertoggle, path, treestore):
        try:
            run_as_root('true')
            b = treestore[path][0] = not treestore[path][0]
            file = treestore[path][2]
            i = treestore[path][3]
            if i == -1:
                parent = treestore.get_iter_from_string(path)
                self.__set_children_toggle(parent, b)
            else:
                child = treestore.get_iter_from_string(path)
                parent = treestore.iter_parent(child)
                self.__enable_repos(b, file, i)
                self.__set_parent_toggle(parent)
            self.__apply()
        except AccessDeniedError:
            pass
    
    def __edited(self, cellrenderertext, path, new_text):
        if self.treestore[path][1] != new_text:
            tmp = self.treestore[path][1]
            self.treestore[path][1] = new_text
            b = self.treestore[path][0]
            file = self.treestore[path][2]
            i = self.treestore[path][3]
            self.__souces_list[file][i] = new_text + '\n'
            self.__enable_repos(b, file, i)
            try:
                self.__apply()
            except AccessDeniedError:
                self.treestore[path][1] = tmp
                self.__souces_list[file][i] = tmp + '\n'
    
    def __add_repos(self, widget):
        print self.addArea.getRepos()
        self.addArea.clearContent()
    
    def __set_parent_toggle(self, parent):
        child = self.treestore.iter_children(parent)
        while child:
            if not self.treestore.get_value(child, 0):
                self.treestore.set_value(parent, 0, False)
                return
            child = self.treestore.iter_next(child)
        self.treestore.set_value(parent, 0, True)
        return
    
    def __set_children_toggle(self, parent, b):
        child = self.treestore.iter_children(parent)
        while child:
            self.treestore.set_value(child, 0, b)
            file = self.treestore.get_value(child, 2)
            i = self.treestore.get_value(child, 3)
            self.__enable_repos(b, file, i)
            child = self.treestore.iter_next(child)
    
    def __enable_repos(self, b, file, i):
        if b:
            if self.__souces_list[file][i].startswith('#'):
                self.__souces_list[file][i] = self.__souces_list[file][i][1:]
        else:
            if not self.__souces_list[file][i].startswith('#'):
                self.__souces_list[file][i] = '#' + self.__souces_list[file][i]
                
class AddReposArea(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self, False)
        
        self.officialBox = gtk.HBox(False)
        self.thirdPartyBox = gtk.HBox(False)
        self.currentBox = self.officialBox
        
        self.officialBox.entry = entry = gtk.Entry()
        self.officialBox.pack_start(entry)
        
        self.pack_start(self.currentBox)
    
    def getRepos(self):
        if self.currentBox == self.officialBox:
            return self.officialBox.entry.get_text()
        
    def clearContent(self):
        self.officialBox.entry.set_text('')