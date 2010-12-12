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

import sys, os, urllib2, gtk, thread, time, re
from lib import *
from libu import *

icons_pack_version = 6

class DownloadIconsWindow(gtk.Window):
    url = 'http://ailurus.googlecode.com/files/appicons_v%s.tar.gz' % icons_pack_version
    filename = '/tmp/appicons.tar.gz'
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.explainlabel = gtk.Label(_('Downloading icons of other open-source projects.\n') + 
                                      _('Do not download any icon of close-source projects or proprietary software.\n'))
        self.explainlabel.set_alignment(0, 0.5)
        self.urllabel = gtk.Label()
        self.urllabel.set_alignment(0, 0.5)
        self.progressbar = gtk.ProgressBar()
        vbox = gtk.VBox(False, 10)
        vbox.set_border_width(10)
        vbox.pack_start(self.explainlabel)
        vbox.pack_start(self.urllabel)
        vbox.pack_start(self.progressbar)
        self.add(vbox)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.realize() # show "busy" cursor
        try: self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        except: print_traceback()
        self.connect('delete-event', self.before_delete_event)
        self.show_all()

        self.can_exit = False
        self.exception = None
        self.set_title(_('Downloading extra icons'))
        self.urllabel.set_text(self.url)
        self.progressbar.set_text('0%')
        self.percentage = 0

    def before_delete_event(self, *w):
        if self.can_exit == False: return True
        else: sys.exit()
    
    def get_length_from_header(self, header_string):
        list = re.findall(r'Content-Length: ([0-9]+)', header_string)
        try:
            value = int(list[0])
            return value
        except: # not happen if download from googlecode. happens if download from file:// 
            return 1

    def download_thread(self):
        try:
            try:
                if Config.get_use_proxy(): enable_urllib2_proxy()
                else: disable_urllib2_proxy()
            except:
                print_traceback()
            in_file = urllib2.urlopen(self.url)
            header_string = str(in_file.info())
            total_size = self.get_length_from_header(header_string)
            blocks_transferred = 0
            block_size = 1024
            out_file = open(self.filename, 'w')
            while True:
                block = in_file.read(block_size)
                if len(block) == 0: break # EOF
                else:
                    blocks_transferred += 1
                    out_file.write(block)
                    self.percentage = min(1, float(blocks_transferred * block_size) / total_size)
        except:
            self.exception = sys.exc_info()
        finally:
            self.can_exit = True

    def show_percentage(self):
        self.progressbar.set_fraction(self.percentage)
        self.progressbar.set_text('%s%%' % int(self.percentage*100))
    
    def main_thread(self):
        while self.can_exit == False:
            self.show_percentage()
            while gtk.events_pending(): gtk.main_iteration()
            time.sleep(0.1)
        self.show_percentage()
        while gtk.events_pending(): gtk.main_iteration()
        if self.exception:
            exception_happened(*self.exception)
            gtk.main() # show exception dialog
        else:
            try:
                self.install_icons()
            except:
                exception_happened(*sys.exc_info())
                gtk.main()
            else:
                notify(' ', _('Icons are successfully installed.'))
                sys.exit()
    
    def install_icons(self):
        # install app icons in $HOME/.config, therefore authentication is not required
        Config.make_config_dir()
        appicons_path = Config.config_dir
        os.chdir(appicons_path)
        run('tar xf ' + self.filename)

if __name__ == '__main__':
    import ctypes # change_task_name
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, 'ailurus_icon_downloader', 0, 0, 0)
    if get_output('pgrep -u $USER ailurus_icon_downloader', True): # detect_running_instances
        sys.exit(1) # another instance is running, therefore I exit

    window = DownloadIconsWindow()
    thread.start_new_thread(window.download_thread, ())
    gtk.gdk.threads_enter()
    window.main_thread()
    gtk.gdk.threads_leave()

