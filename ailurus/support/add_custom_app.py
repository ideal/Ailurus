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
import pango

from lib import *
from libu import *
from loader import *
from libapp import *
from libsetting import *
    
class AddCustomAppDialog(gtk.Dialog):
    liststore_all_pkg = gtk.ListStore(str)

    def clear(self):
        self.entry_detail.set_text('')
        self.entry_name.set_text('')
        self.entry_pkg.set_text('')
        self.entry_pkgs.set_text('')

    def show_message_box(self, title, content):
        dialog = gtk.MessageDialog(type = gtk.MESSAGE_ERROR,
                                   buttons = gtk.BUTTONS_OK)
        dialog.set_title(title)
        dialog.set_markup(content)
        dialog.run()
        dialog.destroy()

    def __cancel(self, widget):
        self.response(gtk.RESPONSE_REJECT)

    def __get_category(self):
        s = self.combo_category.get_active_text()
        for c in Category.all():
            if c.text == s:
                return c.category
        return 'Other'   

    def __submit(self, button):
        dict={}
        if 'classname' in self.dict:
            dict['classname'] = self.dict['classname']
        else:
            dict['classname'] = 'C_%d' % Config.get_custom_appobj_counter_value()
            Config.increase_customapp_counter_value()
        if getattr(self, 'new_icon_path', ''):
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.new_icon_path)
            pixbuf.save(Config.config_dir + '%s.png' % dict['classname'], 'png')
            if 'classname' in self.dict:
                obj = self.dict['appobj']
                obj.logo_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.new_icon_path, 32, 32)
        dict['__doc__'] = self.entry_name.get_text()
        dict['detail'] = self.entry_detail.get_text()
        
        desktop_env = DISTRIBUTION
        dict[desktop_env] = self.entry_pkgs.get_text()
        if dict[desktop_env] == '':
            self.show_message_box(_('Error'), _('Package name should not be empty!'))
            return
        if dict['__doc__'] == '':
            self.show_message_box(_('Error'), _('Application name should not be empty!'))
            return
        try:
            
            if 'classname' not in self.dict:
                dict['category'] = self.__get_category()
                AppObjs.add_new_appobj_from_dict(dict)
            else:                    
                dict['category'] = self.dict['category'].replace(self.origin_category, self.__get_category())
                obj = self.dict['appobj']
                obj.__doc__ = dict['__doc__']
                obj.detail = dict['detail']
                obj.category = dict['category']
                obj.pkgs = dict[DISTRIBUTION]
                obj.self_check()
                obj.fill()
            CustomApps.add_appobj_from_dict(dict)
        except:
            print_traceback()
        self.response(gtk.RESPONSE_ACCEPT)
        
    def __add_pkg(self, button, entry_pkgs_to_install, entry):
        to_add = entry.get_text()
        if to_add:
            exists = entry_pkgs_to_install.get_text().split()
            if not to_add in exists:
                if to_add in BACKEND.get_existing_pkgs_set():
                    new_text = entry_pkgs_to_install.get_text() + ' ' + entry.get_text()
                    new_text = new_text.strip()
                    entry_pkgs_to_install.set_text(new_text)
                else:
                    self.show_message_box(_('Error'), _('Package is not in repository!'))
        entry.set_text('')
        
    def __pkgname_callback(self, entry):
        self.__add_pkg(None, self.entry_pkgs, self.entry_pkg)
    
    def __choose_icon(self, widget, new_path):
        self.new_icon_path = new_path
    
    def __build_bottom_box(self):
        button_submit = gtk.Button(stock = gtk.STOCK_OK)
        button_submit.connect('clicked', self.__submit)
        button_cancel = gtk.Button(stock = gtk.STOCK_CANCEL)
        button_cancel.connect('clicked', self.__cancel)

        bottom_box = gtk.HBox(False, 10)
        bottom_box.pack_end(button_cancel, False)
        bottom_box.pack_end(button_submit, False)

        return bottom_box
        
    def __init__(self, dict={}):
        # labels
        label_name = gtk.Label(_('Name:'))
        label_name.set_alignment(0, 0.5)
        label_pkgs_to_install = gtk.Label(_('Packages to install:'))
        label_pkgs_to_install.set_alignment(0, 0.5)
        label_add_pkg_to_list = gtk.Label(_('Add package to list:'))
        label_add_pkg_to_list.set_alignment(0,0.5)
        label_detail = gtk.Label(_('Detail:'))
        label_detail.set_alignment(0,0.5)
        label_category = gtk.Label(_('Category:'))
        label_category.set_alignment(0,0.5)

        # entries
        self.entry_pkgs = entry_pkgs = gtk.Entry()
        self.entry_name = entry_name = gtk.Entry()
        entry_name.set_max_length(50)
        self.entry_pkg = entry_pkg = gtk.Entry()
        entry_pkg.connect("activate",self.__pkgname_callback)
        pkg_completion = gtk.EntryCompletion()
        entry_pkg.set_completion(pkg_completion)
        pkg_completion.set_text_column(0)
        pkg_completion.set_minimum_key_length(3)
        pkg_completion.set_model(self.liststore_all_pkg)
        button_add_pkg = stock_image_only_button(gtk.STOCK_ADD)
        button_add_pkg.connect("clicked", self.__add_pkg, self.entry_pkgs, entry_pkg)
        self.entry_detail = entry_detail = gtk.Entry()
        entry_detail.set_max_length(50)

        # hbox_add_pkg
        hbox_add_pkg = gtk.HBox(False, 3)
        hbox_add_pkg.pack_start(entry_pkg)
        hbox_add_pkg.pack_start(button_add_pkg, False)

        # combo
        self.combo_category = combo_category = gtk.combo_box_entry_new_text()

        # table
        table = gtk.Table()
        table.set_col_spacings(10)
        table.set_row_spacings(5)
        table.attach(label_name, 0, 1, 0, 1, gtk.FILL, 0)
        table.attach(entry_name, 1, 2, 0, 1)
        table.attach(label_detail, 0, 1, 1, 2, gtk.FILL, 0)
        table.attach(entry_detail, 1, 2, 1, 2)
        table.attach(label_pkgs_to_install, 0, 1, 2, 3, gtk.FILL, 0)
        table.attach(entry_pkgs, 1, 2, 2, 3)
        table.attach(label_add_pkg_to_list, 0, 1, 3, 4, gtk.FILL, 0)
        table.attach(hbox_add_pkg, 1, 2, 3, 4)
        table.attach(label_category, 0, 1, 4, 5, gtk.FILL, 0)
        table.attach(combo_category, 1, 2, 4, 5)
        
        # left_box
        self.icon_chooser = icon_chooser = ImageChooser('/usr/share/pixmaps/', 48, 48)
        icon_chooser.connect('changed',self.__choose_icon)
        left_vbox = gtk.VBox(False)
        left_vbox.pack_start(gtk.Label(), True)
        left_vbox.pack_start(icon_chooser, False)
        left_vbox.pack_start(gtk.Label(), True)
        
        # top_box
        top_box = gtk.HBox(False, 10)
        top_box.pack_start(left_vbox, False)
        top_box.pack_start(table)

        gtk.Dialog.__init__(self,
                            title=_('Edit custom application'),
                            flags=gtk.DIALOG_MODAL|gtk.DIALOG_NO_SEPARATOR)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_border_width(5)
        self.vbox.set_spacing(10)
        self.vbox.pack_start(top_box, False)
        self.action_area.pack_start(self.__build_bottom_box(), False)
        self.show_all()
        
        self.origin_category = self.__get_category()

        self.dict = dict
        if DISTRIBUTION in dict:
            self.entry_pkgs.set_text(dict[DISTRIBUTION] + ' ')
        if '__doc__' in dict:
            self.entry_name.set_text(dict['__doc__'])
        if len(self.liststore_all_pkg) == 0:
            for pkg in BACKEND.get_existing_pkgs_set():
                self.liststore_all_pkg.append([pkg])
        if 'detail' in dict:
            self.entry_detail.set_text(dict['detail'])
        index = 0
        if 'category' in dict:
            target = dict['category']
        else:
            target = ''
        
        category_all = Category.all()
        for i, c in enumerate(category_all):
            if len(target.split()) == 1:
                if c.category == target:
                    index = i
            else:
                if c.category in target.split() and not c.category in ['favourite', 'dustbin']:
                    index = i
            self.combo_category.append_text(c.text)
        self.combo_category.set_active(index)

        if 'classname' in self.dict:
            pixbuf = self.dict['appobj'].logo_pixbuf
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(D + 'sora_icons/default_application_icon.png', 48, 48)
        icon_chooser.display_pixbuf(pixbuf)

if __name__ == '__main__': # debug
    dialog = AddCustomAppDialog()
    dialog.run()
    dialog.destroy()