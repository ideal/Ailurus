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

import gtk, os, sys
from lib import *
from libu import *
from libapp import *
from loader import AppObjs, load_app_objs, CustomApps
from support.add_custom_app import AddCustomAppDialog

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

    def __left_treeview_add_software(self, widget):
        treestore,iter = self.left_treeview.get_selection().get_selected()
        if not iter or not treestore: return

        category = treestore.get_value(iter,2)
        dict = {'category':category}
        dialog = AddCustomAppDialog(dict)
        dialog.run()
        dialog.destroy()

    def __right_treeview_add_software(self, widget):
        treestore, iter = self.left_treeview.get_selection().get_selected()
        if not iter or not treestore: return

        category = treestore.get_value(iter,2)
        dict = {'category':category}
        dialog = AddCustomAppDialog(dict)
        dialog.run()
        dialog.destroy()

    def __right_treeview_edit_software(self, widget):
        treestore, iter = self.right_treeview.get_selection().get_selected()
        appobj = treestore.get_value(iter, 0)
        if not isinstance(appobj, N):
            # TODO: just edit __doc__, detail, category.
            dialog = gtk.MessageDialog(message_format = 'This item will be editable soon. Sorry. :(',
                                       buttons = gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()
        else:
            dict = {'appobj': appobj,
                    'classname': appobj.__class__.__name__,
                    'category': appobj.category,
                    '__doc__': appobj.__doc__,
                    'detail': appobj.detail,
                    DISTRIBUTION: appobj.pkgs,}
            dialog = AddCustomAppDialog(dict)
            dialog.run()
            dialog.destroy()

    def __right_treeview_delete_software(self, widget):
        dict = {}
        treestore, iter = self.right_treeview.get_selection().get_selected()
        appobj = treestore.get_value(iter,0)
        if not isinstance(appobj, N):
            # TODO: remove it?
            dialog = gtk.MessageDialog(message_format = 'This item will be removable soon. Sorry. :(',
                                       buttons = gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()            
            return
        else:
            dict = {'classname': appobj.__class__.__name__,
                    'hide': True}
            CustomApps.add_appobj_from_dict(dict)

            # shall we realize the following code as a method of AppObjs? :)
            AppObjs.appobjs.remove(appobj) # shall we use this line?
            appstore = AppObjs.list_store
            iter = appstore.get_iter_root()
            while iter:
                if appstore.get_value(iter, 0) == appobj:
                    appstore.remove(iter)
                iter = appstore.iter_next(iter)
        
    def __add_software_to_favourite(self, widget):
        treestore, iter = self.right_treeview.get_selection().get_selected()
        appobj = treestore.get_value(iter, 0)
        if not isinstance(appobj, N):
            dialog = gtk.MessageDialog(message_format = 'This item will be able to be added in favourite soon. Sorry. :(',
                                       buttons = gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()
            return
        category_list = appobj.category.split()
        if 'favourite' not in category_list:
            category_list.append('favourite')
            dict = {'classname': appobj.__class__.__name__,
                    'category': ' '.join(category_list)}
            CustomApps.add_appobj_from_dict(dict)

    def __remove_software_from_favourite(self, widget):
        treestore, iter = self.right_treeview.get_selection().get_selected()
        appobj = treestore.get_value(iter, 0)
        if not isinstance(appobj, N):
            dialog = gtk.MessageDialog(message_format = 'This item will be able to be removed from favourite soon. Sorry. :(',
                                       buttons = gtk.BUTTONS_OK)
            dialog.run()
            dialog.destroy()
            return
        category_list = appobj.category.split()
        if 'favourite' in category_list:
            category_list.remove('favourite')
            dict = {'classname': appobj.__class__.__name__,
                    'category': ' '.join(category_list)}
            CustomApps.add_appobj_from_dict(dict)
                
    def __left_tree_view_default_select(self):
        self.left_treeview.get_selection().unselect_all()
        self.left_treeview.expand_all()
        self.left_treeview.get_selection().select_path('2')

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
        toolbar = gtk.HBox(False, 3)
        for text, class_name, icon_path in Category.all_left_class():
            toolbar.pack_start(self.left_class_choose_button(text, class_name, icon_path), False)
        
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
        scrollwindow.add(treeview)
        scrollwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_IN)

        def left_treeview_button_press_event(treeview, event):
            # first try to select the item at mouse position
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                selection = treeview.get_selection()
                path_tuple = treeview.get_path_at_pos(int(event.x), int(event.y))
                
                if path_tuple:
                    selection.select_path(path_tuple[0])
                    item_selected = True
                else:
                    item_selected = False
                
                # if any item is selected, then pop up menu
                if item_selected:
                    add_software = image_stock_menuitem(gtk.STOCK_ADD, _('Add software into this category'))
                    add_software.connect("activate", self.__left_treeview_add_software)
                    popupmenu = gtk.Menu()
                    popupmenu.append(add_software)
                    popupmenu.show_all()
                    if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                        popupmenu.popup(None, None, None, event.button, event.time)
                        return True
            return False
        
        treeview.connect('button_press_event', left_treeview_button_press_event)
        
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(toolbar, False)
        vbox.pack_start(scrollwindow)

        return vbox

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
        
        checkbutton = gtk.CheckButton(_('Do not ask me any more'))
        checkbutton.set_active(not Config.get_do_query_before_install())
        checkbutton.connect('toggled', lambda w: Config.set_do_query_before_install(not w.get_active()))
        
        dialog = gtk.MessageDialog( None,
            gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, _('Are you sure to change your system as follows?') )
        dialog.set_title( _('Confirmation') )
        dialog.format_secondary_markup(msg)
        dialog.vbox.pack_start(left_align(checkbutton), False)
        dialog.vbox.show_all()
        ret = dialog.run()
        dialog.destroy()
        return ret == gtk.RESPONSE_YES

    def app_class_installed_state_changed_by_external(self):
        AppObjs.all_objs_reset_status()
        self.right_treeview.queue_draw()

    def print_failed_objs(self, to_install, to_remove):
        import StringIO, platform, os, traceback
        
        failed_install = [obj for obj in to_install if obj.has_installing_error()]
        failed_remove = [obj for obj in to_remove if obj.has_installing_error()]

        if failed_install==[] and failed_remove==[]: return
        
        message = StringIO.StringIO()
        if failed_install:
            print >>message, '<span color="red">%s</span>' % _('Failed to install:')
            for obj in failed_install:
                print >>message, obj.__doc__,
                if obj.fail_by_download_error():
                    print >>message, _('(network failure. not bug)')
                elif obj.fail_by_user_cancel():
                    print >>message, _('(cancelled by you. not bug)')
                else:
                    print >>message
        if failed_remove:
            print >>message, '<span color="red">%s</span>' % _('Failed to remove:')
            for obj in failed_remove:
                print >>message, obj.__doc__

        error_traceback = StringIO.StringIO()
        print >>error_traceback, platform.dist()
        print >>error_traceback, os.uname()
        print >>error_traceback, 'Ailurus version: ', AILURUS_VERSION
        if len(failed_install):
            for obj in failed_install:
                obj.print_installing_error(error_traceback)
        if len(failed_remove):
            for obj in failed_remove:
                obj.print_installing_error(error_traceback)

        gtk.gdk.threads_enter()
        text_label = gtk.Label()
        text_label.set_markup(message.getvalue())
        text_label.set_alignment(0, 0)

        middle_label = gtk.Label(_('If you think that these errors are caused by a software bug, please tell the developers.') + '\n' +
                                 _('Remember to paste the following debugging information in bug report.'))
        middle_label.set_alignment(0, 0)
        
        textview = gtk.TextView()
        gray_bg(textview)
        textview.set_wrap_mode(gtk.WRAP_WORD)
        textview.get_buffer().set_text(error_traceback.getvalue())
        textview.set_cursor_visible(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(textview)
        
        button_report_bug = image_stock_button(gtk.STOCK_DIALOG_WARNING, _('Report bug') )
        button_report_bug.connect('clicked', lambda w: report_bug() )
        button_copy = image_stock_button(gtk.STOCK_COPY, _('Copy debugging information to clipboard'))
        def clicked():
            buffer = textview.get_buffer()
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            copy_to_clipboard(buffer.get_text(start, end))
        button_copy.connect('clicked', lambda w: clicked())
        button_close = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
        button_close.connect('clicked', lambda w: window.destroy())
        bottom_box = gtk.HBox(False, 10)
        bottom_box.pack_start(button_copy, False)
        bottom_box.pack_start(button_report_bug, False)
        bottom_box.pack_start(button_close, False)
        
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(center_align(text_label), False)
        vbox.pack_start(middle_label, False)
        vbox.pack_start(scroll)
        vbox.pack_start(bottom_box, False)
        window = gtk.Window()
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_title(_('Operations failed'))
        window.set_border_width(10)
        window.add(vbox)
        window.show_all()
        gtk.gdk.threads_leave()
    
    def fix_ubuntu_broken_dependency(self):
        if APT.has_broken_dependency():
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
                                       message_format=_('There are broken packages.\nCommand "apt-get install -f" will be launched to fix error.'))
            dialog.run()
            dialog.destroy()
            run_as_root_in_terminal('apt-get install -f', ignore_error=True)
            APT.cache_changed()
            if APT.has_broken_dependency(): # still cannot fix broken dependency
                dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
                                           message_format=_('Cannot fix broken packages. Installation is cancelled.'))
                dialog.run()
                dialog.destroy()
                return False # exit installing
            while gtk.events_pending(): gtk.main_iteration() # completely destroy dialogs
        return True
    
    def __apply_change_thread(self):
        import os, sys, traceback, StringIO, thread, platform
        try:
            self.__clean_and_show_vte_window()
            run.terminal = self.terminal
            self.terminal.redirect_stdout()
            
            to_install = [ o for o in AppObjs.appobjs if not o.cache_installed and o.showed_in_toggle ]
            to_remove = [ o for o in AppObjs.appobjs if o.cache_installed and not o.showed_in_toggle ]
            
            for obj in AppObjs.appobjs:
                obj.clean_installing_error()
            
            for obj in to_install:
                try:    obj.add_temp_repository()
                except: obj.add_installing_error(sys.exc_info())
                
            for obj in to_install:
                print '\x1b[1;32m', _('Installing:'), obj.__doc__, '\x1b[m'
                try: 
                    reset_dir()
                    obj.install()
                except:
                    obj.add_installing_error(sys.exc_info())
            
            for obj in to_install:
                try:    obj.clean_temp_repository()
                except: obj.add_installing_error(sys.exc_info())

            for obj in to_remove:
                print '\x1b[1;35m', _('Removing:'), obj.__doc__, '\x1b[m'
                try: 
                    reset_dir()
                    obj.remove()
                except:
                    obj.add_installing_error(sys.exc_info())
            
            AppObjs.all_objs_reset_status()
            
            self.print_failed_objs(to_install, to_remove)
            
            delay_notify_firefox_restart(True)
        except:
            print_traceback()
        finally:
            gtk.gdk.threads_enter()
            self.__return_to_app_view()
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
        if UBUNTU or UBUNTU_DERIV:
            try:
                APT.is_cache_lockable()
            except CannotLockAptCacheError, e:
                message_format = _('Check if you are currently running another '
                                   'software management program, e.g. Synaptic or apt-get. '
                                   'Only one program is allowed to make changes at the '
                                   'same time.')
                message_format += '\n' + e.args[0]
                dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK,
                                           message_format=message_format)
                dialog.set_title(_('Cannot lock apt cache'))
                dialog.run()
                dialog.destroy()
                return

        to_install = [ obj for obj in AppObjs.appobjs
                      if obj.cache_installed==False
                      and obj.showed_in_toggle ]
        to_remove = [ obj for obj in AppObjs.appobjs
                     if obj.cache_installed 
                     and obj.showed_in_toggle==False ]
        has_work = len(to_install) or len(to_remove)
        if not has_work: return
        
        if Config.get_do_query_before_install():
            if not self.__query_work(to_install, to_remove):
                return

        run_as_root('true') # require authentication first. do not require authentication any more.
        
        if UBUNTU or UBUNTU_DERIV:
            if self.fix_ubuntu_broken_dependency() == False:
                return

        self.parentwindow.lock()
        import thread
        thread.start_new_thread(self.__apply_change_thread, () )
    
    def __right_sort(self, model, iter1, iter2):
        obj1 = model.get_value(iter1, 0)
        obj2 = model.get_value(iter2, 0)
        cmp_state = cmp(obj1.cache_installed, obj2.cache_installed)
        if cmp_state:
            return cmp_state
        else:
            return cmp(obj1.__doc__, obj2.__doc__)

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
            visible1 = self.right_pane_visible_category in obj.category.split()

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
        
#    def __right_DE_pixbuf_data_func(self, column, cell, model, iter):
#        class0 = model.get_value ( iter, 0 )
#        if hasattr(class0, 'DE'):
#            if class0.DE == 'gnome':
#                cell.set_property('pixbuf', self.DE_GNOME)
#            elif class0.DE == 'kde':
#                cell.set_property('pixbuf', self.DE_KDE)
#        else:
#            cell.set_property('pixbuf', self.DE_DEFAULT)

    def software_state_pixbuf_data_func(self, column, cell, model, iter):
        class0 = model.get_value(iter, 0)
        if class0.cache_installed:
            pixbuf = self.STATE_INSTALLED
        else:
            pixbuf = self.STATE_NOTINSTALLED
        cell.set_property('pixbuf', pixbuf)

    def __launch_quick_setup(self, *w):
        self.parentwindow.lock()
        self.set_sensitive(False)
        def launch():
            import subprocess
            task = subprocess.Popen(['python', A+'/ubuntu/quick_setup.py'])
            task.wait()
            gtk.gdk.threads_enter()
            self.app_class_installed_state_changed_by_external()
            self.parentwindow.unlock()
            self.set_sensitive(True)
            gtk.gdk.threads_leave()

        import thread
        thread.start_new_thread(launch, ())

    def save_softwarelist(self):
        dialog = gtk.FileChooserDialog(title=_('Record the software items you have installed'),
                                       action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK,))
        dialog.set_current_folder(os.environ['HOME'])
        dialog.set_select_multiple(False)
        ret = dialog.run()
        if ret == gtk.RESPONSE_OK:
            path = dialog.get_filename()
            AppObjs.save_installed_items_to_file(path)
            dialog.destroy()
            dialog2 = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
                                        message_format=_('Successfully record the software items to file %s') % path)
            dialog2.run()
            dialog2.destroy()
        else:
            dialog.destroy()
    
    def load_softwarelist(self):
        dialog = gtk.FileChooserDialog(_('Select a software items list'),
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK,))
        dialog.set_current_folder(os.environ['HOME'])
        dialog.set_select_multiple(False)
        ret = dialog.run()
        if ret == gtk.RESPONSE_OK:
            path = dialog.get_filename()
            AppObjs.load_selection_state_from_file(path)
            self.right_treeview.queue_draw()
            dialog.destroy()
            dialog2 = gtk.MessageDialog(buttons=gtk.BUTTONS_OK,
                                        message_format=_('Successfully load file %s') % path)
            dialog2.run()
            dialog2.destroy()
        else:
            dialog.destroy()

    def __right_pane(self):
        self.sync_button = button_sync = image_file_only_button(D+'sora_icons/synchronize.png', 24)
        button_sync.set_tooltip_text(_('Synchronize'))
        button_sync.connect('clicked', lambda w: self.synchronize())

        button_save = image_file_only_button(D+'sora_icons/softwarelist_save.png', 24)
        button_save.set_tooltip_text(_('Record the software items you have installed'))
        button_save.connect('clicked', lambda w: self.save_softwarelist())

        button_load = image_file_only_button(D+'sora_icons/softwarelist_load.png', 24)
        button_load.set_tooltip_text(_('Select the software items according to a saved list'))
        button_load.connect('clicked', lambda w: self.load_softwarelist())

        from support.searchbox import SearchBoxForApp
        searchbox = SearchBoxForApp()
        searchbox.connect('changed', self.__search_content_changed)

        quick_setup_button = image_file_only_button(D+'umut_icons/quick_setup.png', 24)
        quick_setup_button.set_tooltip_text(_('Quickly install popular software'))
        quick_setup_button.connect('clicked', self.__launch_quick_setup)

        self.quick_setup_area = Area()
        self.quick_setup_area.pack_start(quick_setup_button, False)
        self.quick_setup_area.content_visible(UBUNTU or UBUNTU_DERIV)

        button_apply = image_stock_button(gtk.STOCK_APPLY, _('_Apply') )
        button_apply.connect('clicked', self.__apply_button_clicked)

        toolbar = gtk.HBox(False, 3)
        toolbar.pack_start(gtk.VSeparator(), False)
        toolbar.pack_start(button_apply, False)
        toolbar.pack_start(gtk.VSeparator(), False)
        toolbar.pack_start(searchbox, False)
        toolbar.pack_start(gtk.VSeparator(), False)
        toolbar.pack_start(button_sync, False)
        toolbar.pack_start(button_save, False)
        toolbar.pack_start(button_load, False)
        toolbar.pack_start(self.quick_setup_area, False)
        
        import gobject, pango

        self.right_store = treestore = AppObjs.list_store
        self.right_store_filter = treestorefilter = treestore.filter_new()
        treestorefilter.set_visible_func(self.__right_visible_func)
        
        treemodelsort = gtk.TreeModelSort(treestorefilter)
        treemodelsort.set_sort_func(1000, self.__right_sort)
        treemodelsort.set_sort_column_id(1000, gtk.SORT_ASCENDING)

        render_toggle = gtk.CellRendererToggle()
        render_toggle.connect('toggled',self.__right_toggled, treestore, treemodelsort, treestorefilter)
        render_pixbuf = gtk.CellRendererPixbuf()
        render_software_state_pixbuf = gtk.CellRendererPixbuf()
#        render_DE_pixbuf = gtk.CellRendererPixbuf()
#        render_DE_pixbuf.set_property('yalign', 0)
        render_text = gtk.CellRendererText()
        render_text.set_property('ellipsize', pango.ELLIPSIZE_END)

        col_toggle = gtk.TreeViewColumn()
        col_toggle.pack_start(render_toggle,False)
        col_toggle.set_cell_data_func(render_toggle, self.__right_toggle_data_func)

        col_text = gtk.TreeViewColumn()
        col_text.pack_start(render_pixbuf, False)
        col_text.set_cell_data_func(render_pixbuf, self.__right_pixbuf_data_func)
        col_text.pack_start(render_text, True)
        col_text.set_cell_data_func(render_text, self.__right_text_data_func)
        col_text.pack_start(render_software_state_pixbuf, False)
        col_text.set_cell_data_func(render_software_state_pixbuf, self.software_state_pixbuf_data_func)
#        col_text.pack_end(render_DE_pixbuf, False)
#        col_text.set_cell_data_func(render_DE_pixbuf, self.__right_DE_pixbuf_data_func)
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
        
        def left_treeview_button_press_event(treeview, event):
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                # first select the item at mouse position
                selection = treeview.get_selection()
                path_tuple = treeview.get_path_at_pos(int(event.x), int(event.y))
            
                if path_tuple:
                    selection.select_path(path_tuple[0])
                    item_selected = True
                else:
                    item_selected = False

                # then pop up menu
                add_software = image_stock_menuitem(gtk.STOCK_ADD, _('Add a software item'))
                add_software.connect("activate", self.__right_treeview_add_software)
                edit_software = image_stock_menuitem(gtk.STOCK_EDIT, _('Edit'))
                edit_software.connect("activate", self.__right_treeview_edit_software)
                remove_software = image_stock_menuitem(gtk.STOCK_REMOVE, _('Delete'))
                remove_software.connect("activate", self.__right_treeview_delete_software)
                add_to_favourite = image_file_menuitem(_('Add To Favourite'), D+'sora_icons/favourite.png', 16)
                add_to_favourite.connect("activate", self.__add_software_to_favourite)
                remove_from_favourite = gtk.MenuItem(_('Remove From Favourite'))
                remove_from_favourite.connect("activate", self.__remove_software_from_favourite)

                popupmenu = gtk.Menu()
                popupmenu.append(add_software)
                if item_selected:
                    popupmenu.append(edit_software)
                    popupmenu.append(remove_software)
                    popupmenu.append(add_to_favourite)
                    popupmenu.append(remove_from_favourite)
                popupmenu.show_all()
                popupmenu.popup(None, None, None, event.button, event.time)
                return True
            return False
        
        treeview.connect('button_press_event', left_treeview_button_press_event)
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(toolbar, False)
        vbox.pack_start(scroll)
        return vbox

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
    
    def do_refresh_icon(self):
        AppObjs.all_objs_reload_icon()
        self.right_treeview.queue_draw()

    def do_refresh_installing_state(self):
        AppObjs.all_objs_reset_status()
        self.right_treeview.queue_draw()

    def get_preference_menuitems(self):
        set_wget_param = gtk.MenuItem(_("Set download parameters"))
        set_wget_param.connect('activate', lambda w: self.set_wget_parameters())
        
        refresh_icon = gtk.MenuItem(_('Refresh icons of all software items'))
        refresh_icon.connect('activate', lambda w: self.do_refresh_icon())
        
        refresh_state = gtk.MenuItem(_('Refresh installing state of all software items'))
        refresh_state.connect('activate', lambda w: self.do_refresh_installing_state())
        
        return [set_wget_param, refresh_icon, refresh_state]
    
    def __init__(self, parentwindow):
        load_app_objs()
        gtk.VBox.__init__(self, False, 5)
        self.right_treeview = None # A gtk.TreeView in right pane.
        self.right_store = None # A gtk.TreeStore behind self.treeview
        self.right_store_filter = None # A gtk.TreeModelFilter of self.treestore
        self.filter_text = ''
        self.filter_option = ''
        self.right_pane_visible_category = 'all' # string, selected category in the left pane
        self.left_pane_visible_class = 'all' # string, visible class name in the left pane
        self.left_treeview = None # A gtk.TreeView in left pane.
        self.hpaned = hpaned = gtk.HPaned()
        assert hasattr(parentwindow, 'lock')
        assert hasattr(parentwindow, 'unlock')
        self.parentwindow = parentwindow
        from support.terminal import Terminal
        self.terminal = Terminal()
#        self.DE_KDE = get_pixbuf(D + 'umut_icons/kde.png', 16, 16)
#        self.DE_GNOME = get_pixbuf(D + 'umut_icons/gnome.png', 16, 16)
#        self.DE_DEFAULT = blank_pixbuf(16, 16)
        self.STATE_INSTALLED = get_pixbuf(D + 'sora_icons/software_installed.png', 24, 24)
        self.STATE_NOTINSTALLED = get_pixbuf(D + 'sora_icons/software_not_installed.png', 24, 24)

        import os, sys
        self.backup_stdout = os.dup(sys.stdout.fileno())

        hpaned.pack1 ( self.__left_pane(), False, False )
        hpaned.pack2 ( self.__right_pane(), True, False )

        self.status_label = gtk.Label()
        self.status_label.set_alignment(0.5, 0.5)
        self.show_status()

        self.fill_left_treestore()
        self.__left_tree_view_default_select()
        self.pack_start(hpaned)
        self.pack_start(self.status_label, False)
        self.show_all()
    
        self.notify_sync()
    
    def show_status(self):
        num = len(AppObjs.appobjs)
        text = _('%s available items') % num
        self.status_label.set_text(text)
    
    def notify_sync(self):
        from download_icons import icons_pack_version
        if icons_pack_version > Config.get_last_synced_data_version():
            Config.set_last_synced_data_version(icons_pack_version) # do not ask again and again.
            # TODO: display main_view window before dialog
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_YES_NO,
                                       message_format=
                                       _('Would you like to download latest application data from web?'))
            ret = dialog.run()
            dialog.destroy()
            if ret == gtk.RESPONSE_YES:
                self.synchronize()
        
    def synchronize(self):
        import download_icons
        Config.set_last_synced_data_version(download_icons.icons_pack_version)

        import subprocess
        task = subprocess.Popen(['python', A+'/download_icons.py'])
        task.wait()

        self.do_refresh_icon()

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
        all_categories = set()
        for obj in AppObjs.appobjs:
            for c in obj.category.split():
                all_categories.add(c)
        all_categories.add('favourite') # always visible favourite category
        items = Category.all()
        assert items[0].category == 'all'
        items[0].visible = True
        for item in items:
            if item.category in all_categories: item.visible = True
        for item in items:
            if item.visible:
                self.left_store.append(item.to_list())
        
        right_categories = [item.category for item in items]
        for obj in AppObjs.appobjs:
            for c in obj.category.split():
                if c not in right_categories:
                    print obj.__class__.__name__, 'category is wrong'
