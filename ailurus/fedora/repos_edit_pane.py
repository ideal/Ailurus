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
import sys, os
from lib import *
from libu import *
import gobject, pango

class _sections_store(gtk.ListStore):
    def __init__(self):
        gtk.ListStore.__init__(self, gobject.TYPE_PYOBJECT)
        self.reload()
        
    def reload(self):
        self.clear()
        self.repo_objs = FedoraReposFile.all_repo_objs()
        for o in self.repo_objs:
            for s in o.sections:
                self.append([s])

    def write(self):
        for o in self.repo_objs:
            o.write()
    
    def delete(self, section):
        iter = self.get_iter_first()
        while iter:
            if section == self.get_value(iter, 0):
                self.remove(iter)
                break
            iter = self.iter_next(iter)
        section.delete()
    
    def get_custom_repo(self):
        for o in self.repo_objs:
            if o.filename() == 'custom.repo':
                return o
        new = FedoraReposFile(FedoraReposFile.full_path('custom.repo'))
        self.repo_objs.append(new)
        return new
    
    def add_custom_section(self):
        template = ['baseurl=http://',
                    'gpgcheck=1',
                    'gpgkey=file://',
                    'enabled=1',]
        custom = self.get_custom_repo()
        i = 1
        while custom.has_section('custom%s' % i):
            i += 1
        section_name = 'custom%s' % i
        section = FedoraReposSection(['['+section_name+']',
                                      'name=%s'%section_name]
                                     +template, 
                                      custom)
        self.append([section])
        custom.append_section(section)
        return section_name

class _sections_list_box(gtk.VBox):
    __gsignals__ = {
                    'section_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
                    'section_selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
                    'repos_changed'   : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, []),
                    }
    
    def r_enabled_cell_function(self, column, cell, model, iter):
        section = model.get_value(iter, 0)
        if section != None:
            assert isinstance(section, FedoraReposSection)
            cell.set_property('active', section.enabled())

    def r_enabled_toggled(self, render, path):
        path = self.sorted_store.convert_path_to_child_path(path)
        section = self.sections_store[path][0]
        enabled = section.enabled()
        section.set_enabled(not enabled)
        self.emit('section_changed', section)
    
    def r_name_cell_function(self, column, cell, model, iter):
        section = model.get_value(iter, 0)
        if section != None:
            assert isinstance(section, FedoraReposSection)
            cell.set_property('text', section.name)
    
    def sort_by_enabled(self, model, iter1, iter2):
        section1 = model.get_value(iter1, 0)
        section2 = model.get_value(iter2, 0)
        if section1 and section2: 
            return -cmp(section1.enabled(), section2.enabled()) or cmp(section1.name, section2.name)
        else: return 0
    
    def sort_by_name(self, model, iter1, iter2):
        section1 = model.get_value(iter1, 0)
        section2 = model.get_value(iter2, 0)
        if section1 and section2: return cmp(section1.name, section2.name)
        else: return 0
    
    def section_selected(self, selection, treeview):
        store, iter = selection.get_selected()
        if iter == None:
            self.emit('section_selected', None)
        else:
            section = store.get_value(iter, 0)
            self.emit('section_selected', section)
    
    def delete_selected(self):
        selection = self.view.get_selection()
        store, iter = selection.get_selected()
        if iter:
            section = store.get_value(iter, 0)
            self.sections_store.delete(section)
            self.emit('section_selected', None)
            self.emit('repos_changed')
    
    def __init__(self, store):
        self.sections_store = store
        assert isinstance(self.sections_store, _sections_store)
        self.sorted_store = gtk.TreeModelSort(self.sections_store)
        self.sorted_store.set_sort_func(1000, self.sort_by_enabled)
        self.sorted_store.set_sort_func(1001, self.sort_by_name)
        self.sorted_store.set_sort_column_id(1000, gtk.SORT_ASCENDING)
        
        r_enabled = gtk.CellRendererToggle()
        r_enabled.connect('toggled', self.r_enabled_toggled)
        r_enabled.set_property('xalign', 0.5)
        c_enabled = gtk.TreeViewColumn()
        c_enabled.set_title(_('Enabled'))
        c_enabled.pack_start(r_enabled)
        c_enabled.set_cell_data_func(r_enabled, self.r_enabled_cell_function)
        c_enabled.set_sort_column_id(1000)
        
        r_name = gtk.CellRendererText()
        r_name.set_property('ellipsize', pango.ELLIPSIZE_END)
        c_name = gtk.TreeViewColumn()
        c_name.set_title(_('Name'))
        c_name.pack_start(r_name)
        c_name.set_cell_data_func(r_name, self.r_name_cell_function)
        c_name.set_sort_column_id(1001)
        
        view = self.view = gtk.TreeView(self.sorted_store)
        view.append_column(c_enabled)
        view.append_column(c_name)
        view.get_selection().set_mode(gtk.SELECTION_SINGLE)
        view.get_selection().connect('changed', self.section_selected, view)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(view)
        scroll.set_size_request(300, -1)
        
        gtk.VBox.__init__(self, False, 5)
        self.pack_start(scroll)

    def redraw_view(self):
        self.view.queue_draw()

    def select_section(self, section_name):
        store = self.sorted_store
        iter = store.get_iter_first()
        while iter:
            section = store.get_value(iter, 0)
            if section.name == section_name:
                selection = self.view.get_selection()
                selection.select_iter(iter)
                path = store.get_path(iter)
                self.view.scroll_to_cell(path)
                return
            iter = store.iter_next(iter)

class _section_content_box(gtk.VBox):
    __gsignals__ = {
                    'section_changed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
                    }
    
    def __init__(self):
        gtk.VBox.__init__(self, False, 5)

        name_entry = self.name_entry = gtk.Entry()
        name_entry.connect('changed', self.content_changed)

        buffer = self.buffer = gtk.TextBuffer()
        buffer.create_tag('section_name', font='DejaVu Serif', scale=pango.SCALE_LARGE)
        buffer.create_tag('key', foreground='purple')
        buffer.create_tag('value', foreground='blue')
        self.buffer.connect('changed', self.content_changed)
        view = self.view = gtk.TextView(buffer)
        view.set_wrap_mode(gtk.WRAP_CHAR)
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(view)
        
        self.pack_start(name_entry, False)
        self.pack_start(scroll)
        
        self.current_section = None
        self.show_section(None)

        import re
        self.name_pattern = re.compile(r'\[(\S+)\]')
        self.kv_pattern = re.compile(r'([^=]+)=(.+)')
    
    def show_text_in_buffer(self, text):
        buffer = self.buffer
        buffer.set_text(''); end = buffer.get_end_iter()
        lines = text.split('\n'); lines = [l for l in lines if l]
        if self.name_pattern.match(lines[0]): # lines[0] is section name
            section_name = lines[0][1:-1]
            self.name_entry.set_text(section_name) # display section name

        for line in lines[1:]:
            match = self.kv_pattern.match(line)
            if match:
                k, v = match.group(1), match.group(2)
                buffer.insert_with_tags_by_name(end, k, 'key')
                buffer.insert(end, '=')
                buffer.insert_with_tags_by_name(end, v, 'value')
            else:
                buffer.insert(end, line)
            buffer.insert(end, '\n')
                
    def show_section(self, section):
        self.current_section = None
        if section: # show section
            assert isinstance(section, FedoraReposSection)
            self.show_text_in_buffer(section.to_string())
            self.name_entry.set_sensitive(True)
            self.view.set_sensitive(True)
        else: # no selected section
            self.buffer.set_text(_('(please select a repository)'))
            self.name_entry.set_text('')
            self.name_entry.set_sensitive(False)
            self.view.set_sensitive(False)
        self.current_section = section
        
    def buffer_content(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end)

    def content_changed(self, widget):
        if self.current_section is not None:
            self.current_section.set_new_content_as('[%s]\n' % self.name_entry.get_text().strip() + self.buffer_content())
            self.emit('section_changed', self.current_section)

class FedoraReposEditPane(gtk.VBox):
    icon = D+'sora_icons/m_repository_configure.png'
    text = _('Repositories')

    def add_custom_section(self):
        section_name = self.sections_store.add_custom_section()
        self.sections_list_box.select_section(section_name)

    def __init__(self, main_view):
        self.sections_store = _sections_store()
        self.sections_list_box = _sections_list_box(self.sections_store)
        self.section_content_box = _section_content_box()
        self.sections_list_box.connect('section_selected',
                                       lambda w, section:
                                           self.section_content_box.show_section(section))
        self.sections_list_box.connect('section_changed',
                                       lambda w, section:
                                           self.section_content_box.show_section(section))
        self.section_content_box.connect('section_changed',
                                          lambda *w: self.sections_list_box.redraw_view())

        paned = gtk.HPaned()
        paned.pack1(self.sections_list_box)
        paned.pack2(self.section_content_box)
        
        gtk.VBox.__init__(self, False, 5)
        self.pack_start(paned)
        
        button_reload = image_stock_button(gtk.STOCK_REVERT_TO_SAVED, _('Reset'))
        button_reload.connect('clicked', lambda *w: self.sections_store.reload())
        button_delete = image_stock_button(gtk.STOCK_DELETE, _('Delete'))
        button_delete.connect('clicked', lambda *w: self.sections_list_box.delete_selected())
        button_add = image_stock_button(gtk.STOCK_ADD, _('Append'))
        button_add.connect('clicked', lambda *w: self.add_custom_section())
        button_save = image_stock_button(gtk.STOCK_SAVE, _('Save'))
        button_save.connect('clicked', lambda *w: self.sections_store.write())
        button_save.set_sensitive(False)
        
        button_box = gtk.HBox(False, 10)
        button_box.pack_start(button_reload, False)
        button_box.pack_start(button_delete, False)
        button_box.pack_start(button_add, False)
        button_box.pack_end(button_save, False)

        self.pack_start(button_box, False)

        self.should_save = False
        def section_changed(*w):
            self.should_save = True
            button_save.set_sensitive(True)
        self.sections_list_box.connect('section_changed', section_changed)
        self.sections_list_box.connect('repos_changed', section_changed)
        self.section_content_box.connect('section_changed', section_changed)

        def delete_event(*w):
            if self.should_save:
                d = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO,
                                      message_format=_('Repositories have been changed. Would you like to save them?'))
                if d.run() == gtk.RESPONSE_YES:
                    self.sections_store.write()
        import atexit
        atexit.register(delete_event)
