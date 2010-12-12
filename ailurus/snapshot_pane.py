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
import gtk, gobject
import sys, os
from lib import *
from libu import *

class _snapshot_store(gtk.ListStore):
    def __init__(self):
        gtk.ListStore.__init__(self, gobject.TYPE_PYOBJECT) # date & comment
        self.set_sort_func(1000, self.sort_by_time)
        self.reload()
    
    def reload(self):
        self.clear()
        ss = Snapshot.all_snapshots()
        for s in ss:
            self.append([s])

    def sort_by_time(self, model, iter1, iter2):
        s1 = model.get_value(iter1, 0)
        s2 = model.get_value(iter2, 0)
        if s1 and s2: return cmp(s1.time(), s2.time())
        else: return 0

    def create_snapshot_now(self):
        s = Snapshot.new_snapshot()
        self.append([s])

    def remove(self, snapshot):
        assert isinstance(snapshot, Snapshot)
        iter = self.get_iter_first()
        while iter:
            if self.get_value(iter, 0) == snapshot:
                gtk.ListStore.remove(self, iter)
                snapshot.remove()
                return
            else:
                iter = self.iter_next(iter)
        raise Exception # program bug!

class _snapshot_list(gtk.VBox):
    __gsignals__ = {
                'snapshot_selected': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_PYOBJECT]),
                }
    
    def __init__(self, store):
        assert isinstance(store, _snapshot_store)
        self.store = store
        self.sorted_store = gtk.TreeModelSort(self.store)
        self.sorted_store.set_sort_func(1000, self.store.sort_by_time)
        self.sorted_store.set_sort_column_id(1000, gtk.SORT_DESCENDING)
        
        r_time = gtk.CellRendererText()
        r_comment = gtk.CellRendererText()
        r_comment.set_property('editable', True)
        r_comment.connect('edited', self.r_comment_edited)
        c_date = gtk.TreeViewColumn()
        c_date.set_title(_('Date'))
        c_date.pack_start(r_time, False)
        c_date.set_cell_data_func(r_time, self.r_time_cell_function)
        c_date.set_sort_column_id(1000)
        c_comment = gtk.TreeViewColumn()
        c_comment.set_title(_('Comment'))
        c_comment.pack_start(r_comment)
        c_comment.set_cell_data_func(r_comment, self.r_comment_cell_function)
        view = self.view = gtk.TreeView(self.sorted_store)
        view.set_rules_hint(True)
        view.append_column(c_date)
        view.append_column(c_comment)
        view.get_selection().set_mode(gtk.SELECTION_SINGLE)
        view.get_selection().connect('changed', self.row_selected, view)
        view.set_tooltip_text(_('Double click to edit comment'))
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scroll.add(view)
        scroll.set_size_request(300, -1)
        
        gtk.VBox.__init__(self, False, 5)
        self.pack_start(gtk.Label(_('snapshots')), False)
        self.pack_start(scroll)

    def r_comment_edited(self, render, path, new_text):
        snapshot = self.sorted_store[path][0]
        snapshot.set_comment(new_text)
        self.view.queue_draw()

    def row_selected(self, selection, treeview):
        store, iter = selection.get_selected()
        if iter == None:
            self.emit('snapshot_selected', None)
        else:
            sn = store.get_value(iter, 0)
            self.emit('snapshot_selected', sn)
    
    def r_time_cell_function(self, column, cell, model, iter):
        sn = model.get_value(iter, 0)
        if sn != None:
            assert isinstance(sn, Snapshot)
            cell.set_property('text', time_string(sn.time()))

    def r_comment_cell_function(self, column, cell, model, iter):
        sn = model.get_value(iter, 0)
        if sn != None:
            assert isinstance(sn, Snapshot)
            cell.set_property('text', sn.comment())

    def agree_delete(self):
        d = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                              buttons=gtk.BUTTONS_YES_NO,
                              message_format=_('Are you sure to delete the snapshot?'))
        d.set_default_response(gtk.RESPONSE_YES)
        response = d.run()
        d.destroy()
        return response == gtk.RESPONSE_YES
    
    def remove_selected(self):
        selection = self.view.get_selection()
        model, iter = selection.get_selected()
        if iter and self.agree_delete():
            snapshot = model.get_value(iter, 0)
            assert isinstance(snapshot, Snapshot)
            self.store.remove(snapshot)

class _diff_list(gtk.VBox):
    def r_status1_cell_func(self, column, cell, model, iter):
        installed = model.get_value(iter, 1)
        if installed:
            cell.set_property('text', _('was installed'))
            cell.set_property('foreground', 'blue')
        else:
            cell.set_property('text', _('was removed'))
            cell.set_property('foreground', 'red')

    def r_action_cell_func(self, column, cell, model, iter):
        action = model.get_value(iter, 1)
        if action:
            cell.set_property('text', _('will be removed'))
            cell.set_property('foreground', 'red')
        else:
            cell.set_property('text', _('will be installed'))
            cell.set_property('foreground', 'blue')

    def get_todo(self):
        return self.store2

    def clear_todo(self):
        self.store2.clear()

    def __init__(self):
        from support.multidragview import MultiDragTreeView
        
        self.store1 = gtk.ListStore(str, bool) #package name, currently installed?
        self.store2 = gtk.ListStore(str, bool) #package name, action
                
        r_name1 = gtk.CellRendererText()
        c_name1 = gtk.TreeViewColumn(_('package'))
        c_name1.pack_start(r_name1)
        c_name1.add_attribute(r_name1, 'text', 0)
        c_name1.set_sort_column_id(0)
        
        r_status1 = gtk.CellRendererText()
        c_status1 = gtk.TreeViewColumn()
        c_status1.pack_start(r_status1)
        c_status1.set_cell_data_func(r_status1, self.r_status1_cell_func)
        c_status1.set_sort_column_id(1)
        
        self.view1 = view1 = MultiDragTreeView(self.store1)
        view1.append_column(c_name1)
        view1.append_column(c_status1)
        view1.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        scroll1 = gtk.ScrolledWindow()
        scroll1.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll1.set_shadow_type(gtk.SHADOW_IN)
        scroll1.add(view1)

        r_name2 = gtk.CellRendererText()
        c_name2 = gtk.TreeViewColumn()
        c_name2.pack_start(r_name2)
        c_name2.add_attribute(r_name2, 'text', 0)
        c_name2.set_sort_column_id(0)

        r_action2 = gtk.CellRendererText()
        c_action2 = gtk.TreeViewColumn()
        c_action2.pack_start(r_action2)
        c_action2.set_cell_data_func(r_action2, self.r_action_cell_func)
        c_action2.set_sort_column_id(1)

        self.view2 = view2 = MultiDragTreeView(self.store2)
        view2.append_column(c_name2)
        view2.append_column(c_action2)
        view2.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        scroll2 = gtk.ScrolledWindow()
        scroll2.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll2.set_shadow_type(gtk.SHADOW_IN)
        scroll2.add(view2)
        
        TARGETS = [('treeview_row', gtk.TARGET_SAME_APP, 0)]
        view1.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, TARGETS, gtk.gdk.ACTION_COPY)
        view1.enable_model_drag_dest(TARGETS, gtk.gdk.ACTION_DEFAULT)
        view1.connect('drag_data_get', self.drag_data_get_data)
        view1.connect('drag_data_received', self.drag_data_received_data_dummy)
        view2.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, TARGETS, gtk.gdk.ACTION_MOVE)
        view2.enable_model_drag_dest(TARGETS, gtk.gdk.ACTION_DEFAULT)
        view2.connect('drag_data_get', self.drag_data_get_data)
        view2.connect('drag_data_received', self.drag_data_received_data)

        table = gtk.Table()
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        table.attach(gtk.Label(_('changes')), 0, 1, 0, 1, gtk.FILL, gtk.FILL)
        table.attach(gtk.Label(_('to do')), 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        table.attach(scroll1, 0, 1, 1, 2, gtk.FILL)
        table.attach(scroll2, 1, 2, 1, 2, gtk.FILL)
        
        gtk.VBox.__init__(self, False, 5)
        self.pack_start(table)
        self.set_tooltip_text(_('Drag items from the left box into the right box, then click "apply" button.'))

    def show_difference(self, snapshot):
        self.store1.clear()
        if snapshot:
            assert isinstance(snapshot, Snapshot)
            new_installed, new_removed = snapshot.difference()
            for p in new_installed:
                self.store1.append([p, True])
            for p in new_removed:
                self.store1.append([p, False])
        
    def drag_data_get_data(self, treeview, context, selection, target_id, etime):
        treeselection = treeview.get_selection()
        model, pathlist = treeselection.get_selected_rows()
        import StringIO
        stream = StringIO.StringIO()
        for path in pathlist:
            pkg = model[path][0]
            print >>stream, pkg
        selection.set(selection.target, 8, stream.getvalue())

    def drag_data_received_data_dummy(self, treeview, context, x, y, selection, info, etime):
        treeselection = self.view2.get_selection()
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
            for r in model:
                if r[0] == name: break
            else:
                for r in self.store1:
                    if name == r[0]:
                        value = r[1]; break
                model.append([name, value])

class SnapshotPane(gtk.VBox):
    icon = D+'sora_icons/m_snapshot.png'
    text = _('Snapshots')
    
    def apply_change(self):
        to_remove = []
        to_install = []
        for r in self.diff_list.get_todo():
            if r[1]: to_remove.append(r[0])
            else: to_install.append(r[0])
        try:
            if to_install: BACKEND.install(*to_install)
        except: print_traceback()
        try:
            if to_remove: BACKEND.remove(*to_remove)
        except: print_traceback()
        self.diff_list.clear_todo()
    
    def __init__(self, main_view):
        BACKEND.refresh_cache()
        
        gtk.VBox.__init__(self, False, 5)
        self.pack_start(long_text_label(
            _('Ailurus helps you keep track of what software you have installed/removed. '
              'If you often try to use new software, you do not have to worry about messing up your system now.')), False )

        self.store = _snapshot_store()
        self.snapshot_list = _snapshot_list(self.store)
        self.diff_list = _diff_list()
        self.snapshot_list.connect('snapshot_selected', lambda w, sn: self.diff_list.show_difference(sn))
        paned = gtk.HPaned()
        paned.pack1(self.snapshot_list)
        paned.pack2(self.diff_list)
        
        b_add = image_stock_button(gtk.STOCK_ADD, _('Create a snapshot'))
        b_add.connect('clicked', lambda *w: self.store.create_snapshot_now())
        b_delete = stock_image_only_button(gtk.STOCK_DELETE)
        b_delete.set_tooltip_text(_('Delete selected snapshot'))
        b_delete.connect('clicked', lambda *w: self.snapshot_list.remove_selected())
        b_apply = image_stock_button(gtk.STOCK_APPLY, _('Apply'))
        b_apply.connect('clicked', lambda *w: self.apply_change())
        b_box = gtk.HBox(False, 10)
        b_box.pack_start(b_add, False)
        b_box.pack_start(b_delete, False)
        b_box.pack_start(b_apply, False)
        
        self.pack_start(paned)
        self.pack_start(b_box, False)
