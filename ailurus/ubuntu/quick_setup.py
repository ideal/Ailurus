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
import sys, os
path = os.path.dirname(os.path.abspath(__file__))+'/../'
sys.path.insert(0, path)
os.chdir(path)
from lib import *
from libu import *
from libserver import *
from libapp import *
import gtk

class Adobe_Flash_plugin(_apt_install):
    pkgs = 'flashplugin-installer'

if VERSION < 'lucid':
    class Fix_error_in_49_sansserif_conf(I):
        def installed(self):
            try:
                with open('/etc/fonts/conf.d/49-sansserif.conf') as f:
                    if '>sans-serif<' in f.read():
                        return False
            except IOError: # File does not exist
                pass
            return True
        def install(self):
            with TempOwn('/etc/fonts/conf.d/49-sansserif.conf'):
                with open('/etc/fonts/conf.d/49-sansserif.conf') as f:
                    content = f.read()
                content = content.replace('>sans-serif<', '>sans serif<')
                with open('/etc/fonts/conf.d/49-sansserif.conf', 'w') as f:
                    f.write(content)

class Full_Language_Pack(I):
    def determine_packages(self):
        lang = Config.get_locale().split('_')[0]
        list = [
                'language-pack-' + lang,
                'language-support-fonts-' + lang,
                'language-support-input-' + lang,
                'language-support-translations-' + lang,
                'language-support-' + lang,
                'language-support-writing-' + lang,
                ]
        if GNOME: list.append('language-pack-gnome-' + lang)
        if KDE:   list.append('language-pack-kde-' + lang)
        pkgs = [p for p in list if APT.exist(p) and not APT.installed(p)]
        self.pkgs = pkgs        
    def installed(self):
        self.determine_packages()
        return self.pkgs == []
    def install(self):
        if self.pkgs:
            APT.install(*self.pkgs)
                
WORKS = [
            [_('Search fastest repository'), 'Search_Fastest_Repository', True],
            [_('Full language support and input method'), 'Full_Language_Pack', True],
            [_('Multi-media codec'), 'Multimedia_Codecs', True],
            [_('Decompression software'), 'Enhance_Decompression_Capability', True],
            [_('Stardict'), 'Stardict', True],
            [_(u'Moonlight: an open source implementation of Microsoft® Silverlight'), 'Moonlight', True],
            [_('Flash plugin for web browser') + ' (GNU Gnash)', 'Gnash', False],
            [_('Flash plugin for web browser') + ' (Adobe)', 'Adobe_Flash_plugin', True],
# Some people say that this operation has side effect.
#            [_('Fix Flash plugin font error'), 'Fix_error_in_49_sansserif_conf', True],
            [_('Install hardware drivers'), 'Install_Hardware_Driver', True],
        ]

class SelectWorksDialog(gtk.Dialog):
    def toggled(self, check_button, item):
        item[2] = check_button.get_active()
        
    def __init__(self):
        gtk.Dialog.__init__(self, _('Quickly install popular software'), None, gtk.DIALOG_NO_SEPARATOR, 
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_DELETE_EVENT, 
                             gtk.STOCK_OK, gtk.RESPONSE_OK) )
        image = gtk.Image()
        image.set_from_file(D+'suyun_icons/default.png')
        label = gtk.Label(_('Ailurus helps you quickly install popular software.\n'
                            'Select the software which you would like to install.'))
        title_box = gtk.HBox(False, 15)
        title_box.pack_start(label, False)
        title_box.pack_start(image, False)
        
        check_button_list = []
        for item in WORKS:
            name = item[0]
            check_button = gtk.CheckButton(name)
            check_button.set_active(item[2])
            check_button.connect('toggled', self.toggled, item)
            check_button_list.append(check_button)
        box = gtk.VBox(False, 5)
        box.pack_start(title_box, False)
        for button in check_button_list:
            box.pack_start(button, False)

        self.set_border_width(5)
        self.vbox.pack_start(box)
        self.vbox.show_all()
    
    @classmethod
    def show_dialog(cls):
        dialog = SelectWorksDialog()
        ret = dialog.run()
        dialog.destroy()
        if ret == gtk.RESPONSE_DELETE_EVENT:
            sys.exit()

def acquire_root_privilege():
    print '\x1b[1;36m', _('Acquire root privilege'), '\x1b[m'
    run_as_root('true')

class WaitNetworkDialog(gtk.Dialog):
    def __continuously_ping(self):
        while not self.skip_checking:
            try:
                get_response_time('http://example.com')
                break
            except:
                import time
                time.sleep(3)
        self.destroy()

    def __skip(self):
        self.skip_checking = True

    def __init__(self):
        import thread
        thread.start_new_thread(self.__continuously_ping, () )
        
        self.skip_checking = False
        
        gtk.Dialog.__init__(self,  _('Computer is not connected to Internet'), None, gtk.DIALOG_NO_SEPARATOR,
                                      (gtk.STOCK_QUIT, gtk.RESPONSE_DELETE_EVENT) )
        
        label = gtk.Label( _('Your computer is not connected to Internet.\n'
                                         'Please configure network connections.') )
        
        edit_network_connection = image_stock_button( gtk.STOCK_CONNECT, _('Configure network connections') )
        edit_network_connection.connect('clicked', 
                                                               lambda w: KillWhenExit.add('/usr/bin/nm-connection-editor') )
        
        skip_network_checking = image_stock_button( gtk.STOCK_CANCEL, _('Skip this step'))
        skip_network_checking.connect('clicked', lambda w: self.__skip())
        
        self.set_border_width(5)
        self.vbox.pack_start(label, False, False, 10)
        self.vbox.show_all()
        self.action_area.pack_end(edit_network_connection, False)
        self.action_area.pack_end(skip_network_checking, False)
        self.action_area.show_all()
    
    @classmethod
    def show_check_network_splash(cls):
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_border_width(15)
        color = gtk.gdk.color_parse('#202020')
        window.modify_bg(gtk.STATE_NORMAL, color)
        text = gtk.Label()
        text.set_markup('<span color="yellow">%s</span>' % 
                                   _('Checking whether your computer is connected to Internet ...') )
        window.add(text)
        window.show_all()
        while gtk.events_pending(): gtk.main_iteration()
        return window
    
    @classmethod
    def show_dialog(cls):
        window = WaitNetworkDialog.show_check_network_splash()
        try:
            try:     get_response_time('http://example.com')
            finally: window.destroy()
        except:
            dialog = WaitNetworkDialog()
            ret = dialog.run()
            dialog.destroy()
            if ret == gtk.RESPONSE_DELETE_EVENT: sys.exit()

def show_scan_installed_package_splash():
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

class FastestRepositoryDialog(gtk.Dialog):
    def _before_delete_event(self, *w):
        if self.can_exit == False:
            return True
        return False
    def user_want_to_skip(self, *w):
        self.can_skip = True
        self.can_exit = True
    def __init__(self):
        self.can_exit = False
        self.can_skip = False
        gtk.Dialog.__init__(self, _('Searching the fastest repository'), None, 
                                       gtk.DIALOG_NO_SEPARATOR, None )
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('delete-event', self._before_delete_event)
        self.progress_label = gtk.Label()
        self.progress_bar = gtk.ProgressBar()
        self.timeleft_label = gtk.Label()
        self.button_start = gtk.Button('Start')
        self.button_start.connect('clicked', self.start)
        self.button_skip = gtk.Button(_('Skip this step'))
        self.button_skip.connect('clicked', self.user_want_to_skip)
        self.vbox.set_spacing(10)
        self.set_border_width(10)
        self.vbox.pack_start(self.progress_label, False)
        self.vbox.pack_start(self.progress_bar, False)
        self.vbox.set_size_request(500, -1)
        bottom_box = gtk.HBox(False, 0)
        bottom_box.pack_start(self.timeleft_label, False)
        bottom_box.pack_end(self.button_skip, False)
        self.vbox.pack_start(bottom_box, False)
        self.show_all()
    def refresh_GUI(self):
        pass
    
    def start(self, *w):
        import time
        begintime = time.time()
        def show_result():
            currenttime = time.time()
            len_result = len(result)
            if len_result: server, value = result[-1]
            if len_result ==0: return
            
            #display progress
            total = len(candidate_repos)
            progress = float(len_result) / total
            self.progress_bar.set_fraction(progress)
            self.progress_bar.set_text('%s / %s' % (len_result, total) )
            #display text
            if isinstance(value, float):
                text = _("<span color='black'>Response time of %(server)s is %(value).0f ms.</span>") % {'server' : server, 'value' : value}
            elif value == 'cannot ping' or value == 'unreachable':
                text = _("<span color='black'>Server %s is unreachable.</span>") % server
            self.progress_label.set_markup(text)
            #display time left
            if len_result >= 40 and len_result % 5 == 0 :
                timeleft = float(total-len_result) * (currenttime-begintime) / (len_result)
                text = _("<span color='black'>Time left: %s</span>") % derive_time(int(timeleft))
                self.timeleft_label.set_markup(text)
            
            self.refresh_GUI()

        import threading
        result = []
        threads = []
        candidate_repos = get_candidate_repositories()
        servers = [ e[3] for e in candidate_repos ]
        urls = [ e[2] for e in candidate_repos ]
        #PING servers
        for url,server in zip(urls,servers):
            def alive_threads(threads):
                i = 0
                for t in threads:
                    if t.isAlive(): i += 1
                return i
            while alive_threads(threads)>10:
                import time
                time.sleep(0.1)
                show_result()
                if self.can_skip:
                    self.destroy()
                    while gtk.events_pending(): gtk.main_iteration()
                    return
            thread = PingThread(url, server, result)
            threads.append( thread )
            thread.start()
        for thread in threads:
            if not thread.isAlive(): continue
            thread.join()
            show_result()
            if self.can_skip:
                self.destroy()
                while gtk.events_pending(): gtk.main_iteration()
                return

        #decide fastest server
        min_time = 1e8
        fastest_server = None
        for (server, time) in result:
            if not isinstance(time, float): continue
            if time<min_time:
                min_time = time
                fastest_server = server

        try:
            if not fastest_server: return
            self.progress_label.set_text( _('In order to use the fastest repository, Ailurus will change /etc/apt/sources.list') )
            self.progress_bar.set_text( _('The fastest repository is %s.')%fastest_server )
            
            for e in candidate_repos:
                if e[3] == fastest_server:
                    new_url = e[2]
                    break
            #check whether repositories should be changed
            for repos in APTSource2.official_urls():
                assert ':' in repos
                if repos != new_url: break
            else:
                return
            self.change_server(new_url)
        except:
            print_traceback()
        finally:
            #destroy dialog
            self.can_exit = True
            self.destroy()
            
    def change_server(self, fastest_url):
        'apply the fastest repository'
        run_as_root('cp /etc/apt/sources.list /etc/apt/sources.list.back') # do a back up first
        changes = {}
        for repos in APTSource2.official_urls():
            changes[repos] = fastest_url
        notify( _('Apply the fastest repository:'), fastest_url )
        APTSource2.remove_official_servers()
        APTSource2.add_official_url(fastest_url)
        #apt-get update
        self.progress_label.set_text( _('Run command: "sudo apt-get update"') )
        notify(_('Run "apt-get update". Please wait for few minutes.'), ' ')
        APT.apt_get_update()

class Search_Fastest_Repository:
    def installed(self):
        return False
    def install(self):
        dialog = FastestRepositoryDialog()
        dialog.button_start.emit('clicked')

class Install_Hardware_Driver:
    def installed(self):
        return False
    def install(self):
        spawn_as_root('/usr/bin/jockey-gtk')

def get_obj_by_class_name(name, app_objs):
    assert isinstance(name, str)
    assert isinstance(app_objs, list)
    
    import types
    for o in app_objs:
        assert isinstance(o, types.InstanceType)
        if o.__class__.__name__ == name:
            return o
    g = globals()
    if name in g: 
        c = g[name]
        assert isinstance(c, types.ClassType)
        assert hasattr(c, 'install') and hasattr(c, 'installed')
        return c()
    raise Exception(name)

class DoStuffDialog(gtk.Dialog):
    def func_pixbuf(self, column, cell, model, iter):
        value = model.get_value(iter, 0)
        assert 0 <= value <= 3
        pixbuf = [ self.pixbuf_fail, self.pixbuf_blank, self.pixbuf_started, self.pixbuf_done ] [ value ]
        cell.set_property('pixbuf', pixbuf)
    def refresh_GUI(self):
        pass
    def start(self, *w):
        try:
            run.terminal = self.terminal
            r,w = os.pipe()
            os.dup2(w, sys.stdout.fileno())
            import thread
            thread.start_new_thread(self.terminal.read, (r,) )
            
            for row in self.task_store:
                row[0] = 2
                self.refresh_GUI()
                print '\x1b[1;33m', _('Ongoing:'), row[1], '\x1b[m'
                try:
                    c = row[2]
                    if not c.installed(): c.install()
                    row[0] = 3
                    print '\x1b[1;32m', _('Successful'), '\x1b[m'
                except:
                    row[0] = 0
                    print '\x1b[1;31m', _('Failed'), '\x1b[m'
                    print_traceback()
                print
        finally:
            self.can_exit = True
            sys.stdout.flush()
            os.close(r)
            os.close(w)
            run.terminal = None
            os.dup2(self.backup_stdout, sys.stdout.fileno())

    def refresh_GUI_thread(self):
        while self.can_exit == False:
            if not gtk: break
            while gtk.events_pending(): gtk.main_iteration()
            import time
            time.sleep(0.1)

    def _before_delete_event(self, *w):
        if self.can_exit == False: return True
        return False

    def __init__(self, app_objs):
        self.can_exit = False
        
        import os, sys
        self.backup_stdout = os.dup(sys.stdout.fileno())

        gtk.Dialog.__init__(self, _('Quickly install popular software'), None, gtk.DIALOG_NO_SEPARATOR, None )
        self.connect('delete-event', self._before_delete_event)
        
        self.start_button = gtk.Button()
        self.start_button.connect('clicked', self.start)
        
        import gobject
        # status (0=fail, 1=blank, 2=started, 3=done), text, app_class
        self.task_store = task_store = gtk.ListStore(int, str, gobject.TYPE_PYOBJECT) 
        for text, name, will_do in WORKS:
            if will_do == False: continue
            try:
                c = get_obj_by_class_name(name, app_objs)
                task_store.append([1, text, c])
            except:
                print_traceback()

        self.pixbuf_fail = get_pixbuf(D+'sora_icons/quicksetup_fail.png', 16, 16)
        self.pixbuf_blank = blank_pixbuf(16, 16)
        self.pixbuf_started = get_pixbuf(D+'sora_icons/quicksetup_start.png', 16, 16)
        self.pixbuf_done = get_pixbuf(D+'sora_icons/quicksetup_done.png', 16, 16)

        render_pixbuf = gtk.CellRendererPixbuf()
        render_text = gtk.CellRendererText()
        task_column = gtk.TreeViewColumn()
        task_column.pack_start(render_pixbuf)
        task_column.set_cell_data_func(render_pixbuf, self.func_pixbuf) 
        task_column.pack_start(render_text)
        task_column.add_attribute(render_text, 'text', 1)
        
        task_treeview = gtk.TreeView(task_store)
        task_treeview.append_column(task_column)
        task_treeview.set_headers_visible(False)
        task_treeview.set_rules_hint(True)
        
        task_scroll = gtk.ScrolledWindow()
        task_scroll.set_shadow_type(gtk.SHADOW_IN)
        task_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        task_scroll.add(task_treeview)
        
        from support.terminal_single_thread import Terminal
        self.terminal = terminal = Terminal()
        
        paned = gtk.HPaned()
        paned.pack1(task_scroll, False, True)
        paned.pack2(terminal.get_widget(), True, False)
        paned.set_size_request(900, 500)
        
        self.set_border_width(5)
        self.vbox.pack_start(paned)
        self.show_all()
        
        self.button_close = gtk.Button(stock = gtk.STOCK_CLOSE)
        self.button_close.connect('clicked', lambda *w: self.destroy())
        self.action_area.pack_start(self.button_close) 

def quick_setup():
    SelectWorksDialog.show_dialog()
    acquire_root_privilege()
    WaitNetworkDialog.show_dialog()
    #load app_classes
    window = show_scan_installed_package_splash()
    from loader import load_app_objs
    app_objs = load_app_objs()
    window.destroy()
    #3
    dialog = DoStuffDialog(app_objs)
    import thread
    thread.start_new_thread(dialog.refresh_GUI_thread, () )
    dialog.start_button.emit('clicked')
    #4
    notify( _('All works are done.'), ' ' )
    dialog.action_area.show_all()
    dialog.run()

if __name__ == '__main__':
    gtk.window_set_default_icon_from_file(D+'suyun_icons/default.png')
    import os
    gtk.gdk.threads_init()
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    quick_setup()
