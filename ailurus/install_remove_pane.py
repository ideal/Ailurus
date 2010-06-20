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
import gtk
from lib import *
from libu import *
from libapp import *

class Category:
    def __init__(self, text, icon_path, category, class_name):
        '''category equals "category" attribute value of application class
        class_name is used in left_treeview only'''
        assert isinstance(text, (str, unicode)) and text
        assert isinstance(icon_path, str) and icon_path
        assert isinstance(category, str) and category
        assert isinstance(class_name, str) and class_name
        self.text, self.icon_path, self.category, self.class_name = text, icon_path, category, class_name
        self.icon = get_pixbuf(icon_path, 24, 24)
        self.visible = False
    def to_list(self):
        'Return a list. Add the list into gtk.Liststore'
        return [self.text, self.icon, self.category, self.class_name]
    @classmethod
    def all_left_class(cls):
        'return a list which consists of "text, class_name, icon_path"'
        return [
            (_('Science'), 'science', D+'umut_icons/p_science.png'),
            (_('Develop'), 'develop', D+'sora_icons/p_develop.png'),
            (_('Home'), 'home', D+'sora_icons/p_home.png'),
            (_('Other'), 'other', D+'sora_icons/p_others.png'),
            (_('All'), 'all', D+'sora_icons/p_all.png'),
                ]
    m_all = None
    @classmethod
    def all(cls):
        if cls.m_all: return cls.m_all
        cls.m_all = [
            Category(_('All'), D+'sora_icons/p_all.png', 'all', 'all'),
            # internet
            Category(_('Browser'), D+'sora_icons/p_browser.png', 'browser', 'home'),
            Category(_('Email'), D+'sora_icons/p_email.png', 'email', 'home'),
            Category(_('File sharing'), D+'sora_icons/p_file_sharing.png', 'file_sharing', 'home'),
            Category(_('Chat'), D+'umut_icons/p_chat.png', 'chat', 'home'),
            Category(_('Firefox extension'), D+'umut_icons/p_firefox_extension.png', 'firefox_extension', 'home'),
            Category(_('Flash'), D+'sora_icons/p_flash.png', 'flash', 'home'),
            Category(_('Blog'), D+'sora_icons/p_blog.png', 'blog', 'home'),
            Category(_('RSS'), D+'sora_icons/p_rss.png', 'rss', 'home'),
            Category(_('Internet'), D+'sora_icons/p_internet.png', 'internet', 'home'),
            # multimedia
            Category(_('Player'), D+'sora_icons/p_player.png', 'player', 'home'),
            Category(_('CD burner'), D+'sora_icons/p_cd_burner.png', 'cd_burner', 'home'),
            Category(_('Media editor'), D+'sora_icons/p_media_editor.png', 'media_editor', 'home'),
            # appearance
            Category(_('Panel'), D+'sora_icons/p_panel.png', 'panel', 'home'),
            Category(_('Theme'), D+'sora_icons/p_theme.png', 'theme', 'home'),
            Category(_('Screen widget'), D+'umut_icons/p_candy.png', 'candy', 'home'),
            Category(_('Compiz setting'), D+'sora_icons/p_compiz_setting.png', 'compiz_setting', 'home'),
            # science
            Category(_('Math'), D+'umut_icons/p_math.png', 'math', 'science'),
            Category(_('Statistics'), D+'umut_icons/p_statistics.png', 'statistics', 'science'),
            Category(_('Electronics'), D+'umut_icons/p_electronics.png', 'electronics', 'science'),
            Category(_('Mechanics'), D+'umut_icons/p_mechanics.png', 'mechanics', 'science'),
            Category(_('Geography'), D+'sora_icons/p_geography.png', 'geography', 'science'),
            Category(_('Biology'), D+'sora_icons/p_biology.png', 'biology', 'science'),
            Category(_('LaTeX'), D+'umut_icons/p_latex.png', 'latex', 'science'),
            # programming
            Category(_('IDE'), D+'sora_icons/p_ide.png', 'ide', 'develop'),
            Category(_('Version control'), D+'sora_icons/p_version_control.png', 'version_control', 'develop'),
            Category(_('Library'), D+'sora_icons/p_library.png', 'library', 'develop'),
            Category(_('Embedded system'), D+'umut_icons/p_embedded_system.png', 'embedded_system', 'develop'),
            Category(_('Text editor'), D+'umut_icons/p_text_editor.png', 'text_editor', 'develop'),
            Category(_('Eclipse extension'), D+'sora_icons/p_eclipse_extension.png', 'eclipse_extension', 'develop'),
            Category(_('Programming tool'), D+'sora_icons/p_saber.png', 'saber', 'develop'),
            # business
            Category(_('Business'), D+'sora_icons/p_business.png', 'business', 'home'),
            # design
            Category(_('Design'), D+'sora_icons/p_design.png', 'design', 'develop'),
            Category(_('Drawing'), D+'umut_icons/p_drawing.png', 'drawing', 'develop'),
            Category(_('Typesetting'), D+'umut_icons/p_typesetting.png', 'typesetting', 'develop'),
            # gnome_dedicated
            Category(_('GNOME dedicated'), D+'sora_icons/p_gnome_dedicated.png', 'gnome_dedicated', 'other'),
            # nautilus
            Category(_('Nautilus extension'), D+'sora_icons/p_nautilus_extension.png', 'nautilus_extension', 'other'),
            # simulator
            Category(_('Simulator'), D+'sora_icons/p_simulator.png', 'simulator', 'other'),
            # education
            Category(_('Education'), D+'umut_icons/p_education.png', 'education', 'home'),
            # game
            Category(_('Game'), D+'sora_icons/p_game.png', 'game', 'home'),
            # antivirus
            Category(_('Anti-virus'), D+'sora_icons/p_antivirus.png', 'antivirus', 'home'),
            # others
            Category(_('Others'), D+'sora_icons/p_others.png', 'others', 'other'),
            # tasksel
            Category(_('Establish a server'), D+'umut_icons/p_establish_a_server.png', 'establish_a_server', 'other'),
            # repository
            Category(_('Repository'), D+'sora_icons/p_repository.png', 'repository', 'other'),
                 ]
        return cls.m_all

class Area(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self, False, 3)
        self.content = []
    def pack_start(self, *arg):
        self.content.append(arg[0])
        gtk.HBox.pack_start(self, *arg)
    def content_visible(self, visible):
        assert isinstance(visible, bool)
        for child in self.get_children():
            self.remove(child)
        if visible:
            for child in self.content:
                gtk.HBox.pack_start(self, child, False)
            self.show_all()

class InstallRemovePane(gtk.VBox):
    icon = D+'sora_icons/m_install_remove.png'
    text = _('Install\nSoftware')
    
    def __left_tree_view_default_select(self):
        self.left_treeview.get_selection().unselect_all()
        self.left_treeview.expand_all()
        self.left_treeview.get_selection().select_path('1')

    def __left_pane_changed ( self, treeselection, treeview ):
        model, parent = treeselection.get_selected()
        if parent == None: return
        category = model.get_value(parent, 2)
        self.right_pane_visible_category = category
        self.right_store_filter.refilter()

    def __left_pane_pixbuf(self, column, cell, model, iter):
        category = model.get_value(iter, 2)
        pixbuf = model.get_value(iter, 1)
        if category.startswith('*'): # This is a big class.
            cell.set_property('visible', False)
        else: # This is an item.
            cell.set_property('visible', True)
            cell.set_property('pixbuf', pixbuf)
    
    def __left_pane_text(self, column, cell, model, iter):
        category = model.get_value(iter, 2)
        text = model.get_value(iter, 0)
        if category.startswith('*'): # This is a big class.
            cell.set_property('markup', '<big><b>%s</b></big>'%text)
        else: # This is an item.
            cell.set_property('text', text)

    def __left_pane(self):
        column_expander = gtk.TreeViewColumn()
        column_expander.set_visible(False)
        pixbuf_render = gtk.CellRendererPixbuf()
        text_render = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start ( pixbuf_render, False )
        column.set_cell_data_func(pixbuf_render, self.__left_pane_pixbuf)
        column.pack_start ( text_render, False )
        column.set_cell_data_func(text_render, self.__left_pane_text)
        # each row of liststore contains (title, icon, category, class_name)
        self.left_store = treestore = gtk.ListStore(str, gtk.gdk.Pixbuf, str, str)
        self.left_store_filter = treefilter = treestore.filter_new()
        self.left_store_filter.set_visible_func(self.__left_visible_func)
        self.left_treeview = treeview = gtk.TreeView()
        treeview.append_column(column_expander)
        treeview.append_column(column)
        treeview.set_model(treefilter)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.get_selection().connect('changed', self.__left_pane_changed, treeview )
        treeview.set_headers_visible(False)
        treeview.set_expander_column(column_expander)

        scrollwindow = gtk.ScrolledWindow ()
        scrollwindow.add ( treeview )
        scrollwindow.set_policy ( gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC )
        scrollwindow.set_shadow_type ( gtk.SHADOW_IN )
        return scrollwindow

    def __clean_and_show_vte_window(self):
        gtk.gdk.threads_enter()
        #clean_vte
        self.terminal.terminal.reset(True, True)
        #change_content
        parentbox = self.parent
        for child in parentbox.get_children():
            parentbox.remove(child)
        parentbox.add(self.terminal.get_widget())
        parentbox.show_all()
        gtk.gdk.threads_leave()
    
    def __query_work(self, to_install, to_remove):
        msg = ''
        if len(to_install):
            msg += _('To be installed:\n')
            for obj in to_install: 
                msg += '<span color="blue">%s</span>\n'%obj.__doc__
            msg += '\n'
        if len(to_remove):
            msg += _('To be removed:\n')
            for obj in to_remove: 
                msg += '<span color="red">%s</span>\n'%obj.__doc__
            msg += '\n' 
        
        dialog = gtk.MessageDialog( None,
            gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, _('Are you sure to change your system as follows?') )
        dialog.set_title( _('Confirmation') )
        dialog.format_secondary_markup(msg)
        ret = dialog.run()
        dialog.destroy()
        return ret == gtk.RESPONSE_YES

    def __show_summary(self, s_i, s_r, f_i, f_r):
        msg = _('Summary: \n\n')
        if len(s_i):
            msg += _('Successfully installed:\n')
            for obj in s_i: msg += '<span color="blue">%s</span>\n'%obj.__doc__
            msg += '\n'
        if len(s_r):
            msg += _('Successfully removed:\n')
            for obj in s_r: msg += '<span color="red">%s</span>\n'%obj.__doc__
            msg += '\n'
        if len(f_i):
            msg += _('Failed to install:\n')
            for tup in f_i:
                msg += '<span color="red">%s</span>\n'%tup[0].__doc__
            msg += _('The tracebacks are in the terminal window.\n\n')
        if len(f_r):
            msg += _('Failed to remove:\n')
            for tup in f_r: 
                msg += '<span color="red">%s</span>\n'%tup[0].__doc__
            msg += _('The tracebacks are in the terminal window.\n\n')
        gtk.gdk.threads_enter()
        dialog = gtk.MessageDialog( None,
            0, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK, _('All works finished.') )
        dialog.format_secondary_markup(msg)
        dialog.run()
        dialog.destroy()
        gtk.gdk.threads_leave()

    def app_class_installed_state_changed_by_external(self):
        for obj in self.app_objs:
            obj.showed_in_toggle = obj.cache_installed = obj.installed()
        self.right_treeview.queue_draw()

    def show_error(self, content):
        title_box = gtk.HBox(False, 5)
        import os
        if os.path.exists(D+'umut_icons/bug.png'):
            image = gtk.Image()
            image.set_from_file(D+'umut_icons/bug.png')
            title_box.pack_start(image, False)
        title = gtk.Label( _('Operations failed.\n'
                             'Would you please copy and paste following text into bug report web-page?') )
        title.set_alignment(0, 0.5)
        title_box.pack_start(title, False)
        
        textview = gtk.TextView()
        gray_bg(textview)
        textview.set_wrap_mode(gtk.WRAP_WORD)
        textview.get_buffer().set_text(content)
        textview.set_cursor_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(textview)
        scroll.set_size_request(-1, 500)
        button_report_bug = image_stock_button(gtk.STOCK_DIALOG_WARNING, _('Click here to report bug via web-page') )
        button_report_bug.connect('clicked', lambda w: report_bug() )
        button_copy = image_stock_button(gtk.STOCK_COPY, _('Copy text to clipboard'))
        def clicked():
            clipboard = gtk.clipboard_get()
            buffer = textview.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            clipboard.set_text(buffer.get_text(start, end))
        button_copy.connect('clicked', lambda w: clicked())
        button_close = gtk.Button(_('Close'))
        button_close.connect('clicked', lambda w: window.destroy())
        bottom_box = gtk.HBox(False, 10)
        bottom_box.pack_start(button_report_bug, False)
        bottom_box.pack_start(button_copy, False)
        bottom_box.pack_start(button_close, False)
        
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(title_box, False)
        vbox.pack_start(scroll)
        vbox.pack_start(bottom_box, False)
        window = gtk.Window()
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title(_('Operations failed'))
        window.set_border_width(10)
        window.add(vbox)
        window.show_all()
    
    def __apply_change_thread(self):
        import os, sys, traceback, StringIO, thread, platform
        try:
            error_traceback = StringIO.StringIO()
            print >>error_traceback, platform.dist()
            print >>error_traceback, os.uname()
            print >>error_traceback, 'Ailurus version: ', AILURUS_VERSION
            self.__clean_and_show_vte_window()
            run.terminal = self.terminal
            self.terminal.redirect_stdout()
            f_i = [] # failed to install
            f_r = [] # failed to remove
            
            to_install = [ o for o in self.app_objs if not o.cache_installed and o.showed_in_toggle ]
            to_remove = [ o for o in self.app_objs if o.cache_installed and not o.showed_in_toggle ]
            
            for obj in to_install:
                try:    obj.add_temp_repository()
                except: f_i += [(obj, sys.exc_info())]
                
            for obj in to_install:
                print '\x1b[1;32m', _('Installing:'), obj.__doc__, '\x1b[m'
                try: 
                    reset_dir()
                    obj.install()
                except: f_i += [(obj, sys.exc_info())]
            
            for obj in to_install:
                try:    obj.clean_temp_repository()
                except: f_i += [(obj, sys.exc_info())]

            for obj in to_remove:
                print '\x1b[1;35m', _('Removing:'), obj.__doc__, '\x1b[m'
                try: 
                    reset_dir()
                    obj.remove()
                except: f_r += [(obj, sys.exc_info())]
            
            for o in self.app_objs:
                o.showed_in_toggle = o.cache_installed = o.installed()
            
            for obj in to_install:
                try:
                    if obj.sane: assert obj.cache_installed
                except: f_i += [(obj, sys.exc_info())]
            
            for obj in to_remove:
                try:
                    if obj.sane: assert not obj.cache_installed
                except: f_r += [(obj, sys.exc_info())]
            
            if len(f_i):
                for tup in f_i:
                    print '\x1b[1;31m', _('Failed to install:'), tup[0].__doc__, '\x1b[m'
                    exc = tup[1]
                    print >>error_traceback, tup[0].__doc__
                    traceback.print_exception( exc[0], exc[1], exc[2], file=error_traceback)
            if len(f_r):
                for tup in f_r: 
                    print '\x1b[1;31m', _('Failed to remove:'), tup[0].__doc__, '\x1b[m'
                    exc = tup[1]
                    print >>error_traceback, tup[0].__doc__
                    traceback.print_exception( exc[0], exc[1], exc[2], file=error_traceback)
            print 

            gtk.gdk.threads_enter()
            if len(f_i) or len(f_r): #If any operation failed, we display "Report problems" dialog
                self.show_error(error_traceback.getvalue())
            gtk.gdk.threads_leave()

            delay_notify_firefox_restart(True)
        except:
            print_traceback()
        finally:
            gtk.gdk.threads_enter()
            parentbox = self.terminal.get_widget().parent
            parentbox.pack_start(self.final_box, False)
            parentbox.show_all()
            self.right_treeview.queue_draw()
            self.right_treeview.get_selection().unselect_all()
            gtk.gdk.threads_leave()
            self.terminal.recover_stdout()
            run.terminal = None

    def __return_to_app_view(self, *w):
        self.parentwindow.unlock()
        #change_content
        parentbox = self.terminal.get_widget().parent
        for child in parentbox.get_children():
            parentbox.remove(child)
        parentbox.add(self)
        parentbox.show_all()

    def __apply_button_clicked(self, widget):
        to_install = [ obj for obj in self.app_objs
                      if obj.cache_installed==False
                      and obj.showed_in_toggle ]
        to_remove = [ obj for obj in self.app_objs
                     if obj.cache_installed 
                     and obj.showed_in_toggle==False ]
        has_work = len(to_install) or len(to_remove)
        if not has_work: return
        if not self.__query_work(to_install, to_remove): return

        run_as_root('true') # require authentication first. do not require authentication any more.
        
        self.parentwindow.lock()
        import thread
        thread.start_new_thread(self.__apply_change_thread, () )
    
    def __right_sort ( self, model, iter1, iter2 ):
        obj1 = model.get_value ( iter1, 0 )
        obj2 = model.get_value ( iter2, 0 )
        import types
        assert isinstance ( obj1 , types.InstanceType )
        assert isinstance ( obj2 , types.InstanceType )        
        str1, str2 = obj1.__doc__, obj2.__doc__
        return cmp(str1, str2)

    def __right_toggled(self, render_toggle,path,treestore,treemodelsort,treestorefilter):
        path1 = treemodelsort.convert_path_to_child_path(path)
        path = treestorefilter.convert_path_to_child_path(path1)
        obj = treestore[path][0]
        import types
        assert isinstance(obj, types.InstanceType)
        assert hasattr(obj, 'showed_in_toggle')
        obj.showed_in_toggle = not obj.showed_in_toggle

    def __right_toggle_data_func ( self, column, cell, model, iter ):
        obj = model.get_value(iter, 0)
        cell.set_property('active', obj.showed_in_toggle)

    def __right_text_data_func(self, column, cell, model, iter):
        obj = model.get_value(iter, 0)
        import StringIO
        markup = StringIO.StringIO()
        print >>markup, '<b>%s</b>' % obj.__doc__,
        if obj.cache_installed==False and obj.showed_in_toggle:
            print >>markup, '<span color="blue">(%s)</span>' % _('will install'),
        if obj.cache_installed and obj.showed_in_toggle==False:
            print >>markup, '<span color="red">(%s)</span>' % _('will remove'),
        if obj.detail:
            print >>markup, ''
            print >>markup, obj.detail,
        if obj.download_url:
            print >>markup, ''
            print >>markup, '<small><span color="#0072B2"><u>%s</u></span></small>' % obj.download_url,
        if obj.how_to_install:
            print >>markup, ''
            print >>markup, '<small><span color="#8A00C2">%s</span></small>' % obj.how_to_install,
        cell.set_property('markup', markup.getvalue())

    def __right_visible_func(self, treestore, iter):
        def inside(p, str2):
            return p.search(str2) != None

        assert isinstance(self.right_pane_visible_category, str)
        obj = treestore.get_value(iter, 0)
        if obj == None: return False

        if 'all' == self.right_pane_visible_category:
            visible1 = not obj.this_is_a_repository
        else:
            visible1 = obj.category == self.right_pane_visible_category

        if self.filter_text == '':
            visible2 = True
        elif self.filter_option == 'name':
            visible2 = inside(self.filter_RE, obj.__doc__)
        else: # both
            visible2 = inside(self.filter_RE, obj.__doc__) or inside(self.filter_RE, obj.detail)
        
        return visible1 and visible2

    def __left_visible_func(self, treestore, iter):
        assert isinstance(self.left_pane_visible_class, str)
        class_name = treestore.get_value(iter, 3)
        if class_name == None: return False
        return self.left_pane_visible_class == 'all' or class_name == self.left_pane_visible_class

    def __right_pixbuf_data_func(self, column, cell, model, iter):
        appobj = model.get_value(iter, 0)
        cell.set_property('pixbuf', appobj.logo_pixbuf)
        
    def __right_DE_pixbuf_data_func(self, column, cell, model, iter):
        class0 = model.get_value ( iter, 0 )
        if hasattr(class0, 'DE'):
            if class0.DE == 'gnome':
                cell.set_property('pixbuf', self.DE_GNOME)
            elif class0.DE == 'kde':
                cell.set_property('pixbuf', self.DE_KDE)
        else:
            cell.set_property('pixbuf', self.DE_DEFAULT)
            
    def __launch_quick_setup(self, *w):
        self.parentwindow.lock()
        self.set_sensitive(False)
        def launch():
            import os
            me_path = os.path.dirname(os.path.abspath(__file__))
            with Chdir(me_path) as o:
                import subprocess
                task = subprocess.Popen(['python', 'ubuntu/quick_setup.py'])
                task.wait()
            gtk.gdk.threads_enter()
            self.app_class_installed_state_changed_by_external()
            self.parentwindow.unlock()
            self.set_sensitive(True)
            gtk.gdk.threads_leave()

        import thread
        thread.start_new_thread(launch, ())

    def __right_pane(self):
        import gobject, pango
        self.right_store = treestore = gtk.ListStore(gobject.TYPE_PYOBJECT)
        
        self.right_store_filter = treestorefilter = treestore.filter_new()
        treestorefilter.set_visible_func(self.__right_visible_func)
        
        treemodelsort = gtk.TreeModelSort(treestorefilter)
        treemodelsort.set_sort_func(1000, self.__right_sort)
        treemodelsort.set_sort_column_id(1000, gtk.SORT_ASCENDING)

        render_toggle = gtk.CellRendererToggle()
        render_toggle.connect('toggled',self.__right_toggled, treestore, treemodelsort, treestorefilter)
        render_pixbuf = gtk.CellRendererPixbuf()
        render_DE_pixbuf = gtk.CellRendererPixbuf()
        render_DE_pixbuf.set_property('yalign', 0)
        render_text = gtk.CellRendererText()
        render_text.set_property('ellipsize', pango.ELLIPSIZE_END)

        col_toggle = gtk.TreeViewColumn()
        col_toggle.pack_start(render_toggle,False)
        col_toggle.set_cell_data_func(render_toggle, self.__right_toggle_data_func)

        col_text = gtk.TreeViewColumn()
        col_text.pack_start(render_pixbuf, False)
        col_text.set_cell_data_func(render_pixbuf, self.__right_pixbuf_data_func)
        col_text.pack_start (render_text, True)
        col_text.set_cell_data_func(render_text, self.__right_text_data_func)
        col_text.pack_end(render_DE_pixbuf, False)
        col_text.set_cell_data_func(render_DE_pixbuf, self.__right_DE_pixbuf_data_func)
        col_text.set_sort_column_id(1000)

        self.right_treeview = treeview = gtk.TreeView(treemodelsort)
        treeview.append_column(col_toggle)
        treeview.append_column(col_text)
        treeview.set_rules_hint(True)
        treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        treeview.set_headers_visible(False)

        scroll = gtk.ScrolledWindow()
        scroll.add(treeview)
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        return scroll

    def __search_content_changed(self, widget, text, option):
        self.filter_text = text
        self.filter_option = option
        import re, locale, StringIO
        itext = self.filter_text.decode(locale.getpreferredencoding())
        otext = StringIO.StringIO()
        for char in itext:
            if char in r'.^$*+?{}[]\|()':
                otext.write('\\')
            otext.write(char)
        self.filter_RE = re.compile(otext.getvalue().encode(locale.getpreferredencoding()),
                                    re.IGNORECASE)
        self.right_store_filter.refilter()

    @classmethod
    def set_wget_parameters(cls):
        current_timeout = Config.wget_get_timeout()
        current_tries = Config.wget_get_triesnum()
        
        adjustment_timeout = gtk.Adjustment(current_timeout, 1, 60, 1, 1, 0)
        scale_timeout = gtk.HScale(adjustment_timeout)
        scale_timeout.set_digits(0)
        scale_timeout.set_value_pos(gtk.POS_BOTTOM)
        timeout_label = label_left_align(_('How long after the server does not respond, give up downloading? (in seconds)'))
        
        adjustment_tries = gtk.Adjustment(current_tries, 1, 20, 1, 1, 0)
        scale_tries = gtk.HScale(adjustment_tries)
        scale_tries.set_digits(0)
        scale_tries.set_value_pos(gtk.POS_BOTTOM)
        tries_label = label_left_align(_('How many times does Ailurus try to download the same resource?'))
        
        dialog = gtk.Dialog(
            _('Set Ailurus download parameter'), 
            None, gtk.DIALOG_MODAL|gtk.DIALOG_NO_SEPARATOR, 
            (gtk.STOCK_OK, gtk.RESPONSE_OK) )
        dialog.set_border_width(5)
        dialog.vbox.pack_start(timeout_label, False)
        dialog.vbox.pack_start(scale_timeout, False)
        dialog.vbox.pack_start(tries_label, False)
        dialog.vbox.pack_start(scale_tries, False)
        dialog.vbox.show_all()
        dialog.run()
        new_timeout = int(adjustment_timeout.get_value())
        new_tries = int(adjustment_tries.get_value())
        Config.wget_set_timeout(new_timeout)
        Config.wget_set_triesnum(new_tries)
        dialog.destroy()
    
    def get_preference_menuitems(self):
        def toggled(w):
            visible = w.get_active()
            Config.set_show_sync_area(visible)
            self.sync_area.content_visible(visible)
        show_sync = gtk.CheckMenuItem(_('Show "synchronize" button'))
        show_sync.set_active(Config.get_show_sync_area())
        show_sync.connect('toggled', toggled)
        def toggled(w):
            visible = w.get_active()
            Config.set_show_quick_setup_area(visible)
            self.quick_setup_area.content_visible(visible)
        show_quick_setup = gtk.CheckMenuItem(_('Show "quickly install popular software" button'))
        show_quick_setup.set_active(Config.get_show_quick_setup_area())
        show_quick_setup.connect('toggled', toggled)
    
        set_wget_param = gtk.MenuItem(_("Set download parameters"))
        set_wget_param.connect('activate', lambda w: self.set_wget_parameters())
        
        return [set_wget_param]
# always show sync & quick_setup
#        if UBUNTU or UBUNTU_DERIV: # this feature only support UBUNTU or MINT.
#            return [show_sync, show_quick_setup, set_wget_param]
#        else:
#            return [show_sync, set_wget_param]
    
    def __init__(self, parentwindow, app_objs):
        gtk.VBox.__init__(self, False, 5)
        self.right_treeview = None # A gtk.TreeView in right pane.
        self.right_store = None # A gtk.TreeStore behind self.treeview
        self.right_store_filter = None # A gtk.TreeModelFilter of self.treestore
        self.filter_text = ''
        self.filter_option = ''
        self.right_pane_visible_category = 'all' # string, selected category in the left pane
        self.left_pane_visible_class = 'all' # string, visible class name in the left pane
        self.app_objs = None # objs in self.treestore
        self.left_treeview = None # A gtk.TreeView in left pane.
        self.hpaned = hpaned = gtk.HPaned()
        assert hasattr(parentwindow, 'lock')
        assert hasattr(parentwindow, 'unlock')
        self.parentwindow = parentwindow
        from support.terminal import Terminal
        self.terminal = Terminal()
        self.DE_KDE = get_pixbuf(D + 'umut_icons/kde.png', 16, 16)
        self.DE_GNOME = get_pixbuf(D + 'umut_icons/gnome.png', 16, 16)
        self.DE_DEFAULT = blank_pixbuf(16, 16)

        self.final_box = gtk.VBox(False, 5)
        self.final_box.set_border_width(5)
        self._final_box_text = gtk.Label(_('All works finished. '))
        self._final_box_text.set_alignment(0, 0.5)
        self.final_box.pack_start( self._final_box_text, False )
        _close_button = image_stock_button( gtk.STOCK_CLOSE, _('Close this terminal') )
        _close_button.connect('clicked', self.__return_to_app_view )
        _hbox = gtk.HBox(False, 5)
        _hbox.pack_start(_close_button, False) 
        self.final_box.pack_start(_hbox, False)
        
        import os, sys
        self.backup_stdout = os.dup(sys.stdout.fileno())

        hpaned.pack1 ( self.__left_pane(), False, False )
        hpaned.pack2 ( self.__right_pane(), True, False )

        button_apply = image_stock_button(gtk.STOCK_APPLY, _('_Apply') )
        button_apply.connect('clicked', self.__apply_button_clicked)
        self.sync_button = button_sync = image_file_only_button(D+'sora_icons/synchronize.png', 24)
        button_sync.set_tooltip_text(_('Synchronize'))
        button_sync.connect('clicked', lambda w: self.synchronize())
        self.sync_area = Area()
        self.sync_area.pack_start(gtk.VSeparator(), False)
        self.sync_area.pack_start(button_sync)
        self.sync_area.content_visible( #Config.get_show_sync_area()
                                        True # always show sync
                                      )
        from support.searchbox import SearchBoxForApp
        searchbox = SearchBoxForApp()
        searchbox.connect('changed', self.__search_content_changed)
        quick_setup_button = image_file_only_button(D+'umut_icons/quick_setup.png', 24)
        quick_setup_button.set_tooltip_text(_('Quickly install popular software'))
        quick_setup_button.connect('clicked', self.__launch_quick_setup)
        self.quick_setup_area = Area()
        self.quick_setup_area.pack_start(gtk.VSeparator(), False)
        self.quick_setup_area.pack_start(quick_setup_button, False)
        self.quick_setup_area.content_visible(
#            (UBUNTU or UBUNTU_DERIV) and Config.get_show_quick_setup_area()
             (UBUNTU or UBUNTU_DERIV) # always show quick_setup on Ubuntu
            )

        self.app_objs = app_objs
        for obj in app_objs:
            self.right_store.append([obj])

        toolbar = gtk.HBox(False, 3)
        for text, class_name, icon_path in Category.all_left_class():
            toolbar.pack_start(self.left_class_choose_button(text, class_name, icon_path), False)
        toolbar.pack_start(self.sync_area, False)
        toolbar.pack_start(gtk.VSeparator(), False)
        toolbar.pack_start(searchbox, False)
        toolbar.pack_start(self.quick_setup_area, False)
        toolbar.pack_start(gtk.VSeparator(), False)
        toolbar.pack_start(button_apply, False)

        self.fill_left_treestore()
        self.__left_tree_view_default_select()
        self.pack_start(toolbar, False)
        self.pack_start(hpaned)
        self.show_all()
    
        import thread
        thread.start_new_thread(self.notify_sync, ())
    
    def notify_sync(self):
        if not Config.get_synced():
            gtk.gdk.threads_enter()
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_YES_NO,
                                       message_format=
                                       _('Would you like to download latest application data from web?'))
            ret = dialog.run()
            dialog.destroy()
            Config.set_synced()
            if ret == gtk.RESPONSE_YES:
                self.synchronize()
            gtk.gdk.threads_leave()

    def synchronize(self):
        import subprocess
        path = os.path.dirname(os.path.abspath(__file__)) + '/download_icons.py'
        task = subprocess.Popen(['python', path])
        Config.set_synced()

    def left_class_choose_button_clicked(self, button):
        self.left_pane_visible_class = button.class_name
        self.left_store_filter.refilter()

    def left_class_choose_button(self, text, class_name, icon_path):
        pixbuf = get_pixbuf(icon_path, 24, 24)
        image = gtk.image_new_from_pixbuf(pixbuf)
        button = gtk.Button()
        button.add(image)
        button.class_name = class_name
        button.connect('clicked', self.left_class_choose_button_clicked)
        button.set_tooltip_text(text)
        return button

    def fill_left_treestore(self):
        all_categories = [obj.category for obj in self.app_objs]
        items = Category.all()
        assert items[0].category == 'all'
        items[0].visible = True
        for item in items:
            if item.category in all_categories: item.visible = True
        for item in items:
            if item.visible:
                self.left_store.append(item.to_list())
        
        right_categories = [item.category for item in items]
        for obj in self.app_objs:
            if obj.category not in right_categories:
                print obj.__class__.__name__, 'category is wrong'
