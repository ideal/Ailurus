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
import sys, os
from lib import *
from libu import *
from libserver import *

class FedoraFastestMirrorPane(gtk.VBox):
    icon = D+'sora_icons/m_fastest_repos.png'
    text = _('Fastest\nRepository')

    COUNTRY, ORG, URL, RESPONSE_TIME = range(4)
    NO_PING_RESPONSE = 100000000
    NOT_DETECTED = NO_PING_RESPONSE + 1
    
    def __repository_visibility_function(self, treestore, iter):
        if self.search_content == None:
            return True
        country = treestore.get_value(iter, self.COUNTRY)
        org = treestore.get_value(iter, self.ORG)
        url = treestore.get_value(iter, self.URL)
        return bool( 
             self.search_content.search(country) or 
             self.search_content.search(org) or
             self.search_content.search(url) )

    def __fill_candidate_store(self):
        for item in all_candidate_repositories():
            try: time = ResponseTime.get(item[self.URL])
            except KeyError: time = self.NOT_DETECTED
            item.append(time)
            self.candidate_store.append(item)

    def __get_candidate_repositories_box(self):
        label = gtk.Label(_('All repositories:'))
        label.set_alignment(0, 0)
        from support.searchbox import SearchBox
        searchbox = SearchBox(self.__callback__search_content_changed)
        treeview = self.__get_candidate_repositories_treeview()
        box = gtk.VBox(False, 5)
        box.set_border_width(5)
        box.pack_start(label, False)
        box.pack_start(searchbox, False)
        box.pack_start(treeview)
        return box

    def __callback__search_content_changed(self, itext):
        assert isinstance(itext, str)
        if not itext:
            self.search_content = None
        else:
            import StringIO
            import re
            otext = StringIO.StringIO()
            for char in itext:
                if char in r'.^$+*?{}[]\|()': otext.write('\\')
                otext.write(char)
            self.search_content = re.compile(otext.getvalue(), re.IGNORECASE)
        self.filted_store.refilter()

    def __show_response_time_in_cell(self, column, cell, model, iter):
        value = model.get_value(iter, self.RESPONSE_TIME)
        assert isinstance(value, (int, float))
        value = int(value)
        if value == self.NO_PING_RESPONSE: 
            text = _('No response')
        elif value == self.NOT_DETECTED:
            text = _('Not detected')
        else:
            text = '%s ms' % value
        cell.set_property('text', text)

    def __get_candidate_repositories_treeview(self):
        render_country = gtk.CellRendererText()
        column_country = gtk.TreeViewColumn( _('Country') )
        column_country.pack_start(render_country)
        column_country.add_attribute(render_country, 'text', self.COUNTRY)
        column_country.set_sort_column_id(self.COUNTRY)
        
        render_org = gtk.CellRendererText()
        render_org.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_org = gtk.TreeViewColumn( _('Organization') )
        column_org.pack_start(render_org)
        column_org.add_attribute(render_org, 'text', self.ORG)
        column_org.set_sort_column_id(self.ORG)
        column_org.set_expand(True)
        column_org.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        
        render_url = gtk.CellRendererText()
        render_url.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_url = gtk.TreeViewColumn('URL')
        column_url.pack_start(render_url)
        column_url.add_attribute(render_url, 'text', self.URL)
        column_url.set_sort_column_id(self.URL)
        column_url.set_expand(True)
        column_url.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        
        render_response_time = gtk.CellRendererText()
        render_response_time.set_property('ellipsize', pango.ELLIPSIZE_END)
        column_response_time = gtk.TreeViewColumn( _('Response time') )
        column_response_time.pack_start(render_response_time)
        column_response_time.set_cell_data_func(render_response_time, self.__show_response_time_in_cell)
        column_response_time.set_sort_column_id(self.RESPONSE_TIME)
        
        candidate_treeview = gtk.TreeView(self.sorted_store)
        candidate_treeview.set_rules_hint(True)
        candidate_treeview.append_column(column_country)
        candidate_treeview.append_column(column_org)
        candidate_treeview.append_column(column_url)
        candidate_treeview.append_column(column_response_time)
        candidate_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        candidate_treeview.set_tooltip_text(_('Click mouse right button to display the context menu.'))
        popupmenu = self.__get_popupmenu_for_candidate_repos_treeview(candidate_treeview)
        def button_press_event(w, event):
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                path = w.get_path_at_pos(int(event.x),int(event.y))
                selection = w.get_selection()
                if path == None: selection.unselect_all()
                elif selection.path_is_selected(path[0])==False: 
                    selection.unselect_all()
                    selection.select_path(path[0])
                popupmenu.popup(None, None, None, event.button, event.time)
                return True
            return False
        candidate_treeview.connect('button_press_event', button_press_event)
        
        candidate_scroll = gtk.ScrolledWindow()
        candidate_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        candidate_scroll.set_shadow_type(gtk.SHADOW_IN)
        candidate_scroll.add(candidate_treeview)

        return candidate_scroll

    def __get_popupmenu_for_candidate_repos_treeview(self, treeview):
        detect_speed_of_selected_repos = image_stock_menuitem(gtk.STOCK_FIND,
            _('Detect response time of selected repositories'))
        detect_speed_of_selected_repos.connect('activate', self.__callback__detect_selected_repos_speed, treeview)

        detect_speed_of_all_repos = image_stock_menuitem(gtk.STOCK_FIND,
            _('Detect response time of all repositories'))
        detect_speed_of_all_repos.connect('activate', self.__callback__detect_all_repos_speed)

        use_selected = image_stock_menuitem(
            gtk.STOCK_GO_FORWARD, _('Use selected repositories'))
        use_selected.connect('activate', self.__callback__use_selected_repositories_via_treeview, treeview)
        
        select_all = image_stock_menuitem(gtk.STOCK_SELECT_ALL, _('Select all'))
        select_all.connect('activate', lambda w: treeview.get_selection().select_all())
        select_all_repos_in_this_county = image_stock_menuitem(gtk.STOCK_SELECT_ALL, 
            _('Select all repositories in these countries'))
        select_all_repos_in_this_county.connect('activate', self.__callback__select_all_repos_in_selected_country, treeview)
        
        unselect_all = gtk.MenuItem(_('Unselect all'))
        unselect_all.connect('activate', lambda w: treeview.get_selection().unselect_all())
        
        contact_maintainer = image_stock_menuitem(gtk.STOCK_DIALOG_WARNING, 
            _('If some repositories are not listed above, please click here to tell Ailurus developers.') )
        contact_maintainer.connect('activate', lambda w: report_bug() )
        
        copy_repos = gtk.ImageMenuItem(stock_id = gtk.STOCK_COPY)
        copy_repos.connect('activate', self.__callback__copy_selected_repos, treeview)
        
        popupmenu = gtk.Menu()
        popupmenu.append(use_selected)
        popupmenu.append(detect_speed_of_selected_repos)
        popupmenu.append(detect_speed_of_all_repos)
        popupmenu.append(select_all)
        popupmenu.append(select_all_repos_in_this_county)
        popupmenu.append(unselect_all)
        popupmenu.append(contact_maintainer)
        popupmenu.show_all()
        return popupmenu

    def __callback__copy_selected_repos(self, w, treeview):
        selection = treeview.get_selection()
        model, pathlist = selection.get_selected_rows()
        if pathlist == None or len(pathlist)==0: # select nothing
            return
        
        import StringIO
        msg = StringIO.StringIO()
        for path in pathlist:
            iter = model.get_iter(path)
            print >>msg, model.get_value(iter, self.URL)
        content = msg.getvalue()
        clipboard = gtk.clipboard_get()
        clipboard.set_text(content)
               
    def __callback__detect_selected_repos_speed(self, w, treeview):
        selection = treeview.get_selection()
        model, pathlist = selection.get_selected_rows()
        if pathlist == None or len(pathlist)==0: # select nothing
            return
        
        urls = []
        for path in pathlist:
            iter = model.get_iter(path)
            url = model.get_value(iter, self.URL)
            urls.append(url)
        self.__detect_servers_speed(urls)

    def __callback__detect_all_repos_speed(self, w):
        urls = []
        for row in self.candidate_store:
            urls.append(row[self.URL]) 
        self.__detect_servers_speed(urls)

    def __callback__use_selected_repositories_via_treeview(self, w, treeview):
        selection = treeview.get_selection()
        model, pathlist = selection.get_selected_rows()
        if pathlist == None or len(pathlist)==0: # select nothing
            return
        
        if len(pathlist) > 1: 
            notify(_('Please select one repository only'), ' ')
        else:
            path = pathlist[0]
            iter = model.get_iter(path)
            url = model.get_value(iter, self.URL)
            self.__use_repository(url)

    def __use_repository(self, new_url):
        repo_objs = FedoraReposFile.all_repo_objects()
        for obj in repo_objs:
            obj.change_baseurl(new_url)

    def __callback__select_all_repos_in_selected_country(self, w, treeview):
        selection = treeview.get_selection()
        model, pathlist = selection.get_selected_rows()
        if pathlist == None or len(pathlist)==0: # select nothing
            return
        
        countries = set()
        for path in pathlist:
            iter = model.get_iter(path)
            country = model.get_value(iter, self.COUNTRY)
            countries.add(country)
        
        iter = model.get_iter_first()
        while iter:
            country = model.get_value(iter, self.COUNTRY)
            if country in countries:
                selection.select_path(model.get_path(iter))
            iter = model.iter_next(iter)

    def __show_and_return_widgets_in_progress_box(self):
        progress_label = gtk.Label()
        progress_bar = gtk.ProgressBar()
        for child in self.progress_box.get_children():
            self.progress_box.remove(child)
        self.progress_box.pack_start(progress_label, False)
        self.progress_box.pack_start(progress_bar, False)
        self.progress_box.show_all()
        while gtk.events_pending(): gtk.main_iteration()
        return progress_label, progress_bar

    def __show_result_in_progress_box(self, result, total, progress_label, progress_bar):
        assert isinstance(result, list)
        assert isinstance(total, int)
        
        len_result = len(result)
        if len_result == 0: return
        server, value = result[-1]

        #display progress
        progress = float(len_result) / total
        progress_bar.set_fraction(progress)
        progress_bar.set_text('%s / %s' % (len_result, total) )
        #display text
        if isinstance(value, float):
            text = _("<span color='black'>Response time of %(server)s is %(value).2f ms.</span>") % {'server' : server, 'value' : value}
        elif value == 'cannot ping' or value == 'unreachable':
            text = _("<span color='black'>Server %s is unreachable.</span>") % server
        else:
            raise ValueError(value)
        progress_label.set_markup(text)
        while gtk.events_pending(): gtk.main_iteration()

    def __update_candidate_store_with_ping_result(self, result):
        for i in result:
            url = i[0]
            if isinstance(i[1], float): time = int(i[1])
            else: time = self.NO_PING_RESPONSE
            ResponseTime.set(url, time)
        for row in self.candidate_store:
            url = row[self.URL]
            if url in ResponseTime.map:
                row[self.RESPONSE_TIME] = ResponseTime.get(url)

    def __delete_all_widgets_in_progress_box(self):
        for child in self.progress_box.get_children():
            self.progress_box.remove(child)
            child.destroy()

    def __detect_servers_speed(self, urls):
        assert isinstance(urls, list)
        
        import threading
        result = []
        total = len(urls)
        threads = []

        try:
            self.main_view.lock()
            self.set_sensitive(False)
            progress_label, progress_bar = self.__show_and_return_widgets_in_progress_box()
    
            for url in urls:
                def alive_threads(threads):
                    i = 0
                    for t in threads:
                        if t.isAlive(): i += 1
                    return i
                while alive_threads(threads)>10:
                    import time
                    time.sleep(0.1)
                thread = PingThread(url, url, result) # the second argument should be url, not server. It is used in __update_candidate_store_with_ping_result
                threads.append(thread)
                thread.start()
                self.__show_result_in_progress_box(result, total, progress_label, progress_bar)
            for thread in threads:
                if not thread.isAlive(): continue
                while thread.isAlive() and thread.elapsed_time()<3:
                    import time
                    time.sleep(0.1)
                self.__show_result_in_progress_box(result, total, progress_label, progress_bar)
            self.__update_candidate_store_with_ping_result(result)
    #        self.__write_config_according_to_candidate_store()
            self.__callback__refresh_state_box()
            self.__delete_all_widgets_in_progress_box()
        finally:
            self.main_view.unlock()
            self.set_sensitive(True)

    def __get_state_box(self):
        self.label_state = label_state = gtk.Label()
        label_state.set_alignment(0, 0)
        label_state.set_ellipsize(pango.ELLIPSIZE_END)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_border_width(5)
        scroll.add_with_viewport(label_state)
        scroll.get_child().set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.__callback__refresh_state_box()
        return scroll

    def __callback__refresh_state_box(self):
        print 'refresh_state_box() is not implemented :('

    def __init__(self, main_view):
        assert hasattr(main_view, 'lock')
        assert hasattr(main_view, 'unlock')
        self.main_view = main_view
        ResponseTime.load()
        gtk.VBox.__init__(self, False, 5)
        self.candidate_store = gtk.ListStore(str, str, str, int) # country, org, url, response_time
        self.filted_store = self.candidate_store.filter_new()
        self.search_content = None
        self.filted_store.set_visible_func(self.__repository_visibility_function)
        self.sorted_store = gtk.TreeModelSort(self.filted_store)
        self.sorted_store.set_sort_column_id(self.COUNTRY, gtk.SORT_ASCENDING)
        self.__fill_candidate_store()

        self.progress_box = gtk.VBox(False, 5)
        box2 = gtk.VBox(False, 5)
        box2.pack_start(self.__get_candidate_repositories_box())
        box2.pack_start(self.progress_box, False)
        vpaned = gtk.VPaned()
        vpaned.pack1(self.__get_state_box(), False, True)
        vpaned.pack2(box2, True, True)
        self.pack_start(vpaned)

if __name__ == '__main__':
    path = Config.get_config_dir() + 'response_time_2'
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('a\n1\nb\n2\n')
    ResponseTime.load()
    print ResponseTime.map
    ResponseTime.set('b', 3)
    