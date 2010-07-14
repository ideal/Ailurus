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
import sys, os
from lib import *
from libu import *

class UbuntuAPTRecoveryPane(gtk.VBox):
    icon = D+'sora_icons/m_recovery.png'
    text = _('Recover\nAPT')
    
    def __get_installed_packages_set(self):
        return APT.get_installed_pkgs_set()

    def __make_dir(self):
        Config.make_config_dir()
        return Config.get_config_dir()

    def __make_snapshot(self, *w):
        #get comment
        dialog = gtk.Dialog(
            _('Write comments'), None, gtk.DIALOG_NO_SEPARATOR, 
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK) )
        entry = gtk.Entry()
        def entry_key_pressed(widget, event, dialog):
            if event.keyval == gtk.keysyms.Return:
                dialog.destroy()
                while gtk.events_pending(): gtk.main_iteration()
            return False
        entry.connect('key_press_event', entry_key_pressed, dialog)
        dialog.vbox.pack_start( 
            gtk.Label( _('Would you like to write some comments for this snapshot?') ), False )
        dialog.vbox.pack_start( entry, False )
        dialog.vbox.show_all()
        dialog.run()
        comment = entry.get_text()
        dialog.destroy()
        
        #write snapshot file
        import os
        Dir = self.__make_dir()
        import datetime
        today = datetime.date.today().__str__()
        filename = '%s/apt-snapshot-%s'%(Dir, today)
        with open(filename, 'w') as f:
            for p in self.__get_installed_packages_set():
                print >>f, p

        #write comment
        if comment:
            filename = '%s/comment-%s'%(Dir, today)
            with open(filename, 'w') as f:
                print >>f, comment

        #refresh calendar
        self.__refresh_calendar()

    def __get_day_from_filename(self, filename):
        return int ( filename.replace('apt-snapshot-', '').split('-')[2] )

    def __get_selected_date(self):
        year, month, day = self.calendar.get_date()
        month += 1
        return year, month, day

    def __get_shapshots_in_month(self, year, month):
        import glob
        Dir = self.__make_dir()
        return glob.glob( Dir + 'apt-snapshot-%04d-%02d-*' % (year, month) )

    def __get_shapshot_in_day(self, year, month, day):
        import glob, os
        Dir = self.__make_dir()
        path = Dir + 'apt-snapshot-%04d-%02d-%02d' % (year, month, day)
        if os.path.exists(path): return path
        else: return None

    def __get_comment_in_day(self, year, month, day):
        import glob, os
        Dir = self.__make_dir()
        path = Dir + 'comment-%04d-%02d-%02d' % (year, month, day)
        if os.path.exists(path): return path
        else: return None

    def __refresh_calendar(self):
        'Refresh calendar. Refresh the list of snapshots.'
        year, month, day = self.__get_selected_date()
        self.calendar.clear_marks()
        import StringIO, os
        msg = StringIO.StringIO()
        paths = self.__get_shapshots_in_month(year, month)
        if paths:
            print >>msg, _('Snapshots made in %(year)04d-%(month)02d:')%{'year':year, 'month':month}
            for path in paths:
                filename = os.path.split(path)[1]
                day = self.__get_day_from_filename(filename)
                self.calendar.mark_day(day)
                print >>msg, '%02d-%02d'%(month, day),
                #display comment
                comment_path =  self.__get_comment_in_day(year, month, day)
                if comment_path:
                    with open(comment_path) as f:
                        print >>msg, f.read().strip()
                else:
                    print >>msg 
        else:
            print >>msg, _('There is no snapshot in %(year)04d-%(month)02d.')%{'year':year, 'month':month}
        self.snapshots_detail.set_text( msg.getvalue() )

    def __calendar_month_changed(self, *w):
        self.__refresh_calendar()

    def __show_difference(self, *w):
        self.diff_liststore.clear()
        year, month, day = self.__get_selected_date()
        path = self.__get_shapshot_in_day(year, month, day)
        if path == None: 
            notify( _('There is no snapshot in %(year)04d-%(month)02d-%(day)02d.')
                          %{'year':year, 'month':month, 'day':day}, ' ' )
            return
        past_set = set()
        with open(path) as f:
            for line in f:
                name = line.strip()
                past_set.add(name)
        current_set = self.__get_installed_packages_set()
        if current_set == past_set:
            notify( _('Since %(year)04d-%(month)02d-%(day)02d, there is no change.')
                          %{'year':year, 'month':month, 'day':day}, ' ' )
        else:
            installed = current_set - past_set
            removed = past_set - current_set
            for p in installed:
                self.diff_liststore.append([p, True])
            for p in removed:
                self.diff_liststore.append([p, False])
            self.diff_expander.set_expanded(True)

    def __long_text_label(self, text):
        textview = gtk.TextView()
        gray_bg(textview)
        textview.get_buffer().set_text(text)
        textview.set_wrap_mode(gtk.WRAP_WORD)
        textview.set_cursor_visible(False)
        return textview

    def __init__(self, main_view):
        from support.multidragview import MultiDragTreeView
        
        gtk.VBox.__init__(self, False, 10)
        
        button_make_snapshot = gtk.Button( _('''Create today's snapshot''') )
        button_make_snapshot.connect('clicked', self.__make_snapshot)
        
        self.calendar = calendar = gtk.Calendar()
        calendar.display_options(
            gtk.CALENDAR_SHOW_DAY_NAMES | 
            gtk.CALENDAR_SHOW_HEADING | 
            gtk.CALENDAR_SHOW_WEEK_NUMBERS )
        calendar.connect("month_changed", self.__calendar_month_changed)
        self.snapshots_detail = snapshots_detail = gtk.Label()
        calendar_hbox = gtk.HBox(False, 5)
        calendar_hbox.pack_start(calendar, False)
        calendar_hbox.pack_start(snapshots_detail, False)

        button_show_difference = gtk.Button( _('Show changes since selected day') )
        button_show_difference.connect('clicked', self.__show_difference)

        self.diff_liststore = diff_liststore = gtk.ListStore(str, bool) #package name, currently installed?
        render_name = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn( _('packages') )
        column_name.set_expand(True)
        column_name.pack_start(render_name)
        column_name.add_attribute(render_name, 'text', 0)
        column_name.set_sort_column_id(0)
        render_status = gtk.CellRendererText()
        column_status = gtk.TreeViewColumn( _('changes') )
        column_status.pack_start(render_status)
        column_status.set_sort_column_id(1)
        def render_status_func(column, cell, model, iter):
            installed = model.get_value(iter, 1)

            if installed: text = _('It was installed.')
            else: text = _('It was removed.')
            cell.set_property('text', text )
            
            if installed: cell.set_property('foreground', 'blue')
            else: cell.set_property('foreground', 'red')
        column_status.set_cell_data_func(render_status, render_status_func)
        self.diff_view = diff_view = MultiDragTreeView(diff_liststore)
        diff_view.append_column(column_name)
        diff_view.append_column(column_status)
        diff_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        diff_view_scroll = gtk.ScrolledWindow()
        diff_view_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        diff_view_scroll.set_shadow_type(gtk.SHADOW_IN)
        diff_view_scroll.add(diff_view)

        self.change_liststore = change_liststore = gtk.ListStore(str, bool) #package name, action
        change_render_name = gtk.CellRendererText()
        change_render_action = gtk.CellRendererText()
        change_column_name = gtk.TreeViewColumn( _('package') )
        change_column_name.set_expand(True)
        change_column_name.pack_start(change_render_name)
        change_column_name.add_attribute(change_render_name, 'text', 0)
        change_column_name.set_sort_column_id(0)
        change_column_action = gtk.TreeViewColumn( _('action') )
        change_column_action.pack_start(change_render_action)
        change_column_action.set_sort_column_id(1)
        def change_render_action_func(column, cell, model, iter):
            installed = model.get_value(iter, 1)
            if installed: text = _('will be removed')
            else: text = _('will be installed')
            cell.set_property('text', text)
            if installed: cell.set_property('foreground', 'red')
            else: cell.set_property('foreground', 'blue')
        change_column_action.set_cell_data_func(change_render_action, 
                                                change_render_action_func)
        self.change_view = change_view = MultiDragTreeView(change_liststore)
        change_view.append_column(change_column_name)
        change_view.append_column(change_column_action)
        change_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        change_view_scroll = gtk.ScrolledWindow()
        change_view_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        change_view_scroll.set_shadow_type(gtk.SHADOW_IN)
        change_view_scroll.add(change_view)
        
        TARGETS = [('treeview_row', gtk.TARGET_SAME_APP, 0)]
        diff_view.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                           TARGETS,
                                           gtk.gdk.ACTION_COPY)
        diff_view.enable_model_drag_dest(TARGETS,
                                         gtk.gdk.ACTION_DEFAULT)
        diff_view.connect('drag_data_get', self.drag_data_get_data)
        diff_view.connect('drag_data_received', self.drag_data_received_data_dummy)
        change_view.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                                             TARGETS,
                                             gtk.gdk.ACTION_MOVE)
        change_view.enable_model_drag_dest(TARGETS,
                                           gtk.gdk.ACTION_DEFAULT)
        change_view.connect('drag_data_get', self.drag_data_get_data)
        change_view.connect('drag_data_received', 
                            self.drag_data_received_data)

        table = gtk.Table()
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        table.attach( diff_view_scroll,                            0, 1, 1, 2 )
        table.attach( label_left_align( _('To do:') ),         1, 2, 0, 1, gtk.FILL, gtk.FILL )
        table.attach( change_view_scroll,                      1, 2, 1, 2 )
        bottom_box = gtk.HBox(False, 10)
        bottom_box.pack_start( self.__long_text_label(
         _('In order to revoke packages, '
            'you can drag items from the left box to the right box, '
            'then click the button. ') ) )
        button_apply = image_stock_button( gtk.STOCK_APPLY, _('Apply') )
        button_apply.connect('clicked', self.__revoke)
        bottom_box.pack_start(button_apply, False)
        table.attach( bottom_box,                                  0, 2, 2, 3, gtk.FILL, gtk.FILL)

        self.diff_expander = diff_expander = gtk.Expander( _('Changes:') )
        diff_expander.add(table)
        diff_expander.set_expanded(False)

        self.pack_start( self.__long_text_label( 
            _('Ailurus helps you keep track of what software you have installed/removed. '
              'If you often try to use new software, you do not have to worry about messing up your system now.') ), False )
        self.pack_start( left_align( button_make_snapshot ), False )
        self.pack_start( self.__long_text_label( _('Existing snapshots are displayed in bold font.') ), False )
        self.pack_start( calendar_hbox, False )
        self.pack_start( left_align( button_show_difference ), False )
        self.pack_start( diff_expander )

        self.__refresh_calendar()

    def __revoke(self, *w):
        to_remove = []
        to_install = []
        for r in self.change_liststore:
            if r[1]: to_remove.append(r[0])
            else: to_install.append(r[0])
        if to_remove == [] and to_install == []: return
        try:
            if to_install: APT.install(*to_install)
            if to_remove: APT.remove(*to_remove)
        except:
            print_traceback()
        self.diff_liststore.clear()
        self.change_liststore.clear()

    def drag_data_get_data(self, treeview, context, selection, target_id, etime):
        treeselection = treeview.get_selection()
        model, pathlist = treeselection.get_selected_rows()
        import StringIO
        data = StringIO.StringIO()
        for path in pathlist:
            iter = model.get_iter(path)
            pkg = model.get_value(iter, 0)
            bo = model.get_value(iter, 1)
            print >>data, pkg
        selection.set(selection.target, 8, data.getvalue())
        data.close()

    def drag_data_received_data_dummy(self, treeview, context, x, y, selection, info, etime):
        treeselection = self.change_view.get_selection()
        model, pathlist = treeselection.get_selected_rows()
        pathlist.sort()
        for path in reversed(pathlist):
            iter = model.get_iter(path)
            model.remove(iter)

    def drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
        model = treeview.get_model()
        packed_value = selection.data
        data = packed_value.split('\n')[:-1]
        for name in data:
            exist = False
            for r in model:
                if r[0] == name:
                    exist = True ; break
            if not exist:
                for r in self.diff_liststore:
                    if name == r[0]:
                        value = r[1] ; break
                model.append([name, value])
