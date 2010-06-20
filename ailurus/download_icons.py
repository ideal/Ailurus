#!/usr/bin/env python

import sys, os, urllib, gtk, thread, time
from lib import *
from libu import *

icons_pack_version = 2

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
    
    def reporthook(self, blocks_transferred, block_size, total_size):
        self.percentage = min(1, float(blocks_transferred * block_size) / total_size)

    def download_thread(self):
        try:
            urllib.urlretrieve(self.url, self.filename, self.reporthook)
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
            dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, message_format=_('Please press "OK" button to install icons. Authentication is required.'))
            dialog.run()
            dialog.destroy()
            try:
                self.install_icons()
            except:
                exception_happened(*sys.exc_info())
                gtk.main()
            else:
                dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_OK, message_format=_('Icons are successfully installed. You will see extra icons at the next time when Ailurus starts up.'))
                dialog.run()
                dialog.destroy()
                sys.exit()
    
    def install_icons(self):
        import lib
        icons_path = os.path.dirname(os.path.abspath(lib.__file__))+'/icons/'
        assert os.path.exists(icons_path)
        appicons_path = icons_path + '/appicons/'
        if not os.path.exists(appicons_path):
            run_as_root('mkdir ' + appicons_path)
        os.chdir(appicons_path)
        run_as_root('tar xf ' + self.filename)

if __name__ == '__main__':
    import ctypes # change_task_name
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, 'ailurus_icon_downloader', 0, 0, 0)
    if get_output('pgrep -u $USER ailurus_icon_downloader', True): # detect_running_instances
        sys.exit(1) # another instance is running, therefore I exit
    gtk.gdk.threads_init()
    window = DownloadIconsWindow()
    thread.start_new_thread(window.download_thread, ())
    gtk.gdk.threads_enter()
    window.main_thread()
    gtk.gdk.threads_leave()