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
import gtk, pango
import sys
import os
from lib import *
from libu import *

class CleanUpPane(gtk.VBox):
    icon = D+'sora_icons/m_clean_up.png'
    text = _('Clean up')
    
    def __init__(self, main_view):
        gtk.VBox.__init__(self, False, 10)
        self.pack_start(ReclaimMemoryBox(),False)
        self.pack_start(self.clean_recently_used_document_button(),False)
        self.pack_start(self.clean_ailurus_cache_button(), False)
        self.pack_start(self.clean_nautilus_cache_button(), False)
        if UBUNTU or UBUNTU_DERIV:
            self.pack_start(self.clean_apt_cache_button(), False)
            self.pack_start(UbuntuCleanKernelBox(), False)
            hbox = gtk.HBox(True, 20)
            hbox.pack_start(UbuntuAutoRemovableBox())
            hbox.pack_start(UbuntuDeleteUnusedConfigBox())
            self.pack_start(hbox)
        elif FEDORA:
            self.pack_start(self.clean_rpm_cache_button(), False)
        elif ARCHLINUX:
            self.pack_start(self.clean_pacman_cache_button(), False)

    def get_folder_size(self, folder_path, please_return_integer = False):
        is_string_not_empty(folder_path)
        if os.path.exists(folder_path):
            size = get_output('du -bs ' + folder_path)
            fsize = os.stat(folder_path).st_size
            size = int(size.split('\t', 1)[0]) - fsize # get all file size in folder, not folder size
        else:
            size = 0
        if please_return_integer: return size
        else: return derive_size(size)

    def get_button_text(self, folder_name, folder_path):
        try:
            text = _('Clean %(folder_name)s. Free %(size)s disk space.') % {
                                   'folder_name' : folder_name,
                                   'size' : self.get_folder_size(folder_path) }
        except:
            text = _('Clean %s.' % folder_name)
        return text

    def clean_apt_cache_button(self):
        label = gtk.Label(self.get_button_text(_('APT cache'), '/var/cache/apt/archives'))
        button = gtk.Button()
        button.add(label)
        button.set_sensitive(bool(self.get_folder_size('/var/cache/apt/archives',please_return_integer=True)))
        def __clean_up(button, label):
            notify(_('Run command:'), 'apt-get clean')
            run_as_root_in_terminal('apt-get clean')
            label.set_text(self.get_button_text(_('APT cache'), '/var/cache/apt/archives'))
            button.set_sensitive(bool(self.get_folder_size('/var/cache/apt/archives',please_return_integer=True)))
        button.connect('clicked', __clean_up, label)
        button.set_tooltip_text(_('Command:') + ' sudo apt-get clean')
        return button
    
    def clean_rpm_cache_button(self):
        label = gtk.Label(self.get_button_text(_('RPM cache'), '/var/cache/yum/'))
        button = gtk.Button()
        button.add(label)
        button.set_sensitive(bool(self.get_folder_size('/var/cache/yum/',please_return_integer=True)))
        def __clean_up(button, label):
            notify(_('Run command:'), "yum clean all")
            run_as_root("yum clean all")
            label.set_text(self.get_button_text(_('RPM cache'), '/var/cache/yum/'))
            # Now all enabled repo's cache is clean. However, disabled repo's cache cannot be clean.
            # The remaining disk space is not zero. There are some blank directories in /var/cache/yum/
            # We disable clean button afterwhile.
            button.set_sensitive(False)
        button.connect('clicked', __clean_up, label)
        button.set_tooltip_text(_("Command:") + " yum clean all")
        return button
    
    def clean_ailurus_cache_button(self):
        label = gtk.Label(self.get_button_text(_('Ailurus cache'), '/var/cache/ailurus'))
        button = gtk.Button()
        button.add(label)
        button.set_sensitive(bool(self.get_folder_size('/var/cache/ailurus',please_return_integer=True)))
        def __clean_up(button, label):
            notify(_('Run command:'), 'rm /var/cache/ailurus/* -rf')
            run_as_root('rm /var/cache/ailurus/* -rf')
            label.set_text(self.get_button_text(_('Ailurus cache'), '/var/cache/ailurus'))
            button.set_sensitive(bool(self.get_folder_size('/var/cache/ailurus',please_return_integer=True)))
        button.connect('clicked', __clean_up, label)
        button.set_tooltip_text(_('Command:') + ' sudo rm /var/cache/ailurus/* -rf')
        return button
    
    def clean_pacman_cache_button(self):
        label = gtk.Label(self.get_button_text(_('Pacman cache'), '/var/cache/pacman/pkg'))
        button = gtk.Button()
        button.add(label)
        button.set_sensitive(bool(self.get_folder_size('/var/cache/pacman/pkg',please_return_integer=True)))
        def __clean_up(button, label):
            notify(_('Run command:'), 'rm -rf /var/cache/pacman/pkg/*')
            run_as_root('rm -rf /var/cache/pacman/pkg/*') #"pacman -Sc" does not work
            label.set_text(self.get_button_text(_('Pacman cache'), '/var/cache/pacman/pkg'))
            button.set_sensitive(bool(self.get_folder_size('/var/cache/pacman/pkg',please_return_integer=True)))
        button.connect('clicked', __clean_up, label)
        button.set_tooltip_text(_('Command:') + ' rm -rf /var/cache/pacman/pkg/*') #sudo pacman -Sc
        return button

    def clean_nautilus_cache_button(self):
        path = os.path.expanduser('~/.thumbnails/')
        label = gtk.Label(self.get_button_text(_('Nautilus thumbnail image cache'), path))
        button = gtk.Button()
        button.add(label)
        button.set_sensitive(bool(self.get_folder_size(path, please_return_integer=True)))
        def __clean_up(button, label):
            notify(_('Run command:'), 'rm -rf ~/.thumbnails/*')
            os.system('rm -rf ~/.thumbnails/*')
            label.set_text(self.get_button_text(_('Nautilus thumbnail image cache'), path))
            button.set_sensitive(bool(self.get_folder_size(path, please_return_integer=True)))
        button.connect('clicked', __clean_up, label)
        button.set_tooltip_text(_('Command:') + ' rm -rf ~/.thumbnails/*') #sudo pacman -Sc
        return button

    def clean_recently_used_document_button(self):
        def clear(w):
            import os
            path = os.path.expanduser('~/.recently-used.xbel')
            if os.path.isfile(path):
                os.system("echo '' > ~/.recently-used.xbel")
            else: # is dir
                os.system("rm ~/.recently-used.xbel/* -rf")
            notify(_('Run command:'), _('echo "" > ~/.recently-used.xbel'))
        button = gtk.Button(_('Clear "recent documents" list'))
        button.connect('clicked', clear)
        button.set_tooltip_text(_('Command:') + ' echo "" > ~/.recently-used.xbel')
        return button

class ReclaimMemoryBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 5)
        button_free_memory = gtk.Button( _('Reclaim memory').center(30) )
        button_free_memory.set_tooltip_text(
                                            _('Reclaim memory which stores pagecache, dentries and inodes.\nThis operation is done by "echo 3 >/proc/sys/vm/drop_caches"') )
        button_free_memory.connect('clicked', self.free_memory)
    
        label_info = gtk.Label( _('No more than %s KB of memory can be reclaimed.') % 0 )
        import gobject
        gobject.timeout_add(5000, self.show_cached_memory_amount, label_info)
    
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(button_free_memory)
        hbox.pack_start(label_info, False)
        
        text_buffer = gtk.TextBuffer()
        text_buffer.set_text(_('Linux uses up extra physical memory to work as a disk buffer cache. '
                               'Press the button above to free cache. '
                               'This is not a destructive operation because dirty data will not be freed.\n'
                               'Command: echo 3 >/proc/sys/vm/drop_caches'))
        text_view = gtk.TextView(text_buffer)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(gtk.WRAP_WORD)
        gray_bg(text_view)
        
        self.pack_start(hbox)
        self.pack_start(text_view, False)
        
    def show_cached_memory_amount(self,label):
        try:
            with open('/proc/meminfo') as f:
                for line in f:
                    if line.startswith('Cached:'): 
                        List = line.split()
                        value = int(List[1])
                        break
            label.set_text( _('No more than %s KB of memory can be reclaimed.') % value )
        except:
            print_traceback()
    
        return True
        
    def get_free_memory(self):
        with open('/proc/meminfo') as f:
            for line in f:
                if not line.startswith('MemFree:'): continue
                return int(line.split()[1])
        
    def free_memory(self,*w):
        dest = '/proc/sys/vm/drop_caches'
        import os, tempfile
        if os.path.exists(dest):
            before = self.get_free_memory()
        
            src = tempfile.NamedTemporaryFile('w')
            src.write('3\n')
            src.flush()
            run_as_root('cp %s %s'%(src.name, dest) )
            after = self.get_free_memory()
            amount = max(0, after - before)
            notify(' ', _('%s KB memory was reclaimed.') % amount)

class UbuntuCleanKernelBox(gtk.HBox):
    def version_of_current_kernel(self):
        return os.uname()[2]
    
    def refresh(self):
        self.unused_kernels = []
        import glob, re
        for file_name in glob.glob('/boot/vmlinuz-*'):
            match = re.search(r'vmlinuz-(.+(-[a-z]+)?)', file_name)
            if not match: continue
            version = match.group(1)
            if version == self.version_of_current_kernel(): continue
            self.unused_kernels.append(version)
        self.unused_kernels.sort()
    
        self.liststore.clear()
        for version in self.unused_kernels:
            self.liststore.append([True, version, self.get_size(version)])
        
        self.button_delete.set_sensitive(False)
        
        if self.unused_kernels == []:
            self.view.set_sensitive(False)
            self.liststore.append([True, _('There is no unused Linux Kernel.'), 0])
            self.button_delete.set_sensitive(False)
        
    def get_size(self, version):
        import glob
        files = glob.glob('/boot/*%s*' % version) + glob.glob('/lib/modules/%s' % version)
        ret = 0
        for file in files:
            ret += os.stat(file).st_size
        return ret
    
    def text_data_func(self, column, cell, model, iter):
        keep = model.get_value(iter, 0)
        version = model.get_value(iter, 1)
        size = model.get_value(iter, 2)
        if size: size = derive_size(size)
        else: size = ''
        markup = '<b>%s</b>' % version
        if size:
            markup += '\n'
            markup += size
        if not keep:
            markup += ' ' + _('will be removed')
        cell.set_property('markup', markup)
    
    def toggled(self, render_toggle, path):
        self.liststore[path][0] = not self.liststore[path][0]
        sensitive = False
        for row in self.liststore:
            keep = row[0]
            sensitive = sensitive or not keep
        self.button_delete.set_sensitive(sensitive)
    
    def delete_kernel(self):
        for row in self.liststore:
            keep = row[0]
            if keep: continue
            version = row[1]
            import re
            pure_version = re.match('[0-9.-]+', version).group(0)
            if pure_version.endswith('-'): pure_version = pure_version[:-1]
            to_remove = [p for p in APT.get_installed_pkgs_set() if pure_version in p]
            try:
                if to_remove:
                    APT.remove(*to_remove)
                run_as_root('rm -rf /boot/*%s*' % version)
                run_as_root('rm -rf /lib/modules/%s' % version)
            except:
                print_traceback()
        self.refresh()
    
    def __init__(self):
        self.liststore = gtk.ListStore(bool, str, long) #keep?, version, disk space cost
        render_keep = gtk.CellRendererToggle()
        render_keep.connect('toggled', self.toggled)
        column_keep = gtk.TreeViewColumn()
        column_keep.pack_start(render_keep, False)
        column_keep.add_attribute(render_keep, 'active', 0)
        render_text = gtk.CellRendererText()
        column_text = gtk.TreeViewColumn(_('Unused Linux kernels'))
        column_text.pack_start(render_text, True)
        column_text.set_cell_data_func(render_text, self.text_data_func)
        self.view = view = gtk.TreeView(self.liststore)
        view.append_column(column_keep)
        view.append_column(column_text)
        view.set_rules_hint(True)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(view)
        
        self.button_delete = button_delete = gtk.Button(_('Delete'))
        button_delete.connect('clicked', lambda *w: self.delete_kernel())
        align = gtk.Alignment(0, 0.5)
        align.add(button_delete)

        gtk.HBox.__init__(self, False, 10)
        self.pack_start(scroll)
        self.pack_start(align, False)
        
        self.refresh()

class UbuntuAutoRemovableBox(gtk.HBox):
    def text_data_func(self, column, cell, model, iter):
        keep = model.get_value(iter, 0)
        name = model.get_value(iter, 1)
        size = model.get_value(iter, 2)
        if size: size = derive_size(size)
        else: size = ''
        summary = model.get_value(iter, 3)
        markup = '<b>%s</b> %s' % (name, size)
        if not keep:
            markup += ' ' + _('will be removed')
        if summary:
            markup += '\n'
            markup += summary
        cell.set_property('markup', markup)
    
    def toggled(self, render_toggle, path):
        self.liststore[path][0] = not self.liststore[path][0]
        sensitive = False
        for row in self.liststore:
            keep = row[0]
            sensitive = sensitive or not keep
        self.button_delete.set_sensitive(sensitive)

    def show_scan_installed_package_splash(self):
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_border_width(15)
        color = gtk.gdk.color_parse('#202020')
        window.modify_bg(gtk.STATE_NORMAL, color)
        text = gtk.Label()
        text.set_markup('<span color="yellow"><big><b>%s</b></big>\n%s</span>' % 
                                   ( _('Scanning installed packages.'), _('Please wait a few seconds.') ) )
        window.add(text)
        window.show_all()
        while gtk.events_pending(): gtk.main_iteration()
        return window
    
    def refresh(self, show_splash = False):
        if show_splash:
            window = self.show_scan_installed_package_splash()
        pkgs = APT.get_autoremovable_pkgs()
        if show_splash:
            window.destroy()
        self.liststore.clear()
        self.view.set_model(None)
        for row in pkgs:
            self.liststore.append([True] + row)
        self.view.set_model(self.liststore)
        self.view.set_sensitive(True)
        self.button_unselect_all.set_sensitive(True)
        self.button_delete.set_sensitive(False)
        
        if pkgs == []:
            self.view.set_sensitive(False)
            self.liststore.append([True, _('There is no auto-removable package.'), 0, ''])
            self.button_delete.set_sensitive(False)
            self.button_unselect_all.set_sensitive(False)
    
    def unselect_all(self):
        for row in self.liststore:
            row[0] = False # do not keep
        self.button_delete.set_sensitive( bool(len(self.liststore)) )
    
    def delete_packages(self):
        to_delete = []
        for row in self.liststore:
            keep = row[0]
            name = row[1]
            if not keep: to_delete.append(name)
        if to_delete:
            try: APT.remove(*to_delete)
            except:
                print_traceback()
        self.refresh()
    
    def toggle_data_func(self, column, cell, model, iter):
        keep = model.get_value(iter, 0)
        cell.set_property('active', not keep)
    
    def __init__(self):
        self.liststore = gtk.ListStore(bool, str, long, str) #keep?, name, disk space cost, summary 
        render_keep = gtk.CellRendererToggle()
        render_keep.connect('toggled', self.toggled)
        column_keep = gtk.TreeViewColumn()
        column_keep.pack_start(render_keep, False)
        column_keep.set_cell_data_func(render_keep, self.toggle_data_func)
        render_text = gtk.CellRendererText()
        render_text.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_text = gtk.TreeViewColumn(_('Auto-removable packages'))
        column_text.pack_start(render_text, True)
        column_text.set_cell_data_func(render_text, self.text_data_func)
        self.view = view = gtk.TreeView(self.liststore)
        view.append_column(column_keep)
        view.append_column(column_text)
        view.set_rules_hint(True)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(view)
        
        button_refresh = gtk.Button(_('Refresh'))
        button_refresh.connect('clicked', lambda *w: self.refresh(show_splash = True))
        self.button_unselect_all = button_unselect_all = gtk.Button(_('Select all'))
        button_unselect_all.connect('clicked', lambda *w: self.unselect_all())
        self.button_delete = button_delete = gtk.Button(_('Delete'))
        button_delete.connect('clicked', lambda *w: self.delete_packages())
        button_box = gtk.VBox(False, 5)
        button_box.pack_start(button_refresh, False)
        button_box.pack_start(button_unselect_all, False)
        button_box.pack_start(button_delete, False)
        align = gtk.Alignment(0, 0.5)
        align.add(button_box)

        gtk.HBox.__init__(self, False, 10)
        self.pack_start(scroll)
        self.pack_start(align, False)
        
        view.set_sensitive(False)
        self.liststore.append([True, _('Please press the "Refresh" button.'), 0, ''])
        button_unselect_all.set_sensitive(False)
        button_delete.set_sensitive(False)
        self.refresh()

class UbuntuDeleteUnusedConfigBox(gtk.HBox):
    def text_data_func(self, column, cell, model, iter):
        keep = model.get_value(iter, 0)
        name = model.get_value(iter, 1)
        markup = '<b>%s</b>' % name
        if not keep:
            markup += ' ' + _('will be removed')
        cell.set_property('markup', markup)

    def toggle_data_func(self, column, cell, model, iter):
        keep = model.get_value(iter, 0)
        cell.set_property('active', not keep)
    
    def toggled(self, render_toggle, path):
        self.liststore[path][0] = not self.liststore[path][0]
        sensitive = False
        for row in self.liststore:
            keep = row[0]
            sensitive = sensitive or not keep
        self.button_delete.set_sensitive(sensitive)

    def get_unused_software_configuration(self):
        ret = []
        for line in os.popen('dpkg -l'):
            try:
                state, name = line.split()[:2]
                if state == 'rc':
                    ret.append(name)
            except ValueError: # need more than 1 value to unpack
                pass
        return ret
    
    def refresh(self):
        pkgs = self.get_unused_software_configuration()
        self.liststore.clear()
        self.view.set_model(None)
        for name in pkgs:
            self.liststore.append([True, name])
        self.view.set_model(self.liststore)
        self.view.set_sensitive(True)
        self.button_unselect_all.set_sensitive(True)
        self.button_delete.set_sensitive(False)
        
        if pkgs == []:
            self.view.set_sensitive(False)
            self.liststore.append([True, _('There is no unused software configuration.')])
            self.button_delete.set_sensitive(False)
            self.button_unselect_all.set_sensitive(False)
    
    def unselect_all(self):
        for row in self.liststore:
            row[0] = False # do not keep
        self.button_delete.set_sensitive(bool(len(self.liststore)))
    
    def delete_packages(self):
        to_delete = []
        for row in self.liststore:
            keep = row[0]
            name = row[1]
            if not keep: to_delete.append(name)
        if to_delete:
            try: run_as_root_in_terminal('dpkg --purge ' + ' '.join(to_delete))
            except:
                print_traceback()
        self.refresh()
    
    def __init__(self):
        self.liststore = gtk.ListStore(bool, str) #keep?, name 
        render_keep = gtk.CellRendererToggle()
        render_keep.connect('toggled', self.toggled)
        column_keep = gtk.TreeViewColumn()
        column_keep.pack_start(render_keep, False)
        column_keep.set_cell_data_func(render_keep, self.toggle_data_func)
        render_text = gtk.CellRendererText()
        render_text.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_text = gtk.TreeViewColumn(_('Unused software configuration'))
        column_text.pack_start(render_text, True)
        column_text.set_cell_data_func(render_text, self.text_data_func)
        self.view = view = gtk.TreeView(self.liststore)
        view.append_column(column_keep)
        view.append_column(column_text)
        view.set_rules_hint(True)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(view)
        
        button_refresh = gtk.Button(_('Refresh'))
        button_refresh.connect('clicked', lambda *w: self.refresh())
        self.button_unselect_all = button_unselect_all = gtk.Button(_('Select all'))
        button_unselect_all.connect('clicked', lambda *w: self.unselect_all())
        self.button_delete = button_delete = gtk.Button(_('Delete'))
        button_delete.connect('clicked', lambda *w: self.delete_packages())
        button_box = gtk.VBox(False, 5)
        button_box.pack_start(button_refresh, False)
        button_box.pack_start(button_unselect_all, False)
        button_box.pack_start(button_delete, False)
        align = gtk.Alignment(0, 0.5)
        align.add(button_box)

        gtk.HBox.__init__(self, False, 10)
        self.pack_start(scroll)
        self.pack_start(align, False)

        view.set_sensitive(False)
        self.liststore.append([True, _('Please press the "Refresh" button.')])
        button_unselect_all.set_sensitive(False)
        button_delete.set_sensitive(False)
        self.refresh()
