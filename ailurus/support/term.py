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

# substitude xterm :)

from __future__ import with_statement
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../') # Without this line, error happens. I don't know the reason. *Sigh*
import vte, gtk, StringIO, thread
from lib import *

class Window:
    def delete_event(self, *w):
        if self.can_exit: # set True in self.child_exited(). Means command failed.
            os._exit(1)
        else:
            return True
    def __init__(self):
        self.can_exit = False # set True in self.child_exited()
        self.terminal = terminal = vte.Terminal()
        terminal.connect('child-exited', lambda *w: self.child_exited()) 
        self.scrollwindow = scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scroll.add_with_viewport(terminal)
        self.window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        gtk.window_set_default_icon_from_file(D+'suyun_icons/default.png')
        window.set_title(_('Ailurus terminal'))
        window.set_position(gtk.WIN_POS_CENTER)
        window.add(scroll)
        window.connect('delete-event', self.delete_event)
        window.show_all()
        window.realize()
    def child_exited(self):
        exit_status = self.terminal.get_child_exit_status()
        if exit_status:
            text = self.terminal.get_text(lambda *w: True)
            with open('/tmp/ailurus_subprocess_dump', 'w') as f:
                print >>f, text
            os.chmod('/tmp/ailurus_subprocess_dump', 0666)
            self.can_exit = True
            self.terminal.feed('\n\r'
                               '\x1b[1;31m%s\x1b[m' % _('Command failed. Please close this window.'))
            # do not close window if child process exit abnormally
        else:
            os._exit(0)
    def populate_path(self, env):
        try: path = env['PATH'].split(':')
        except KeyError: path = []
        for item in ['/usr/local/sbin', '/usr/local/bin', '/usr/sbin', '/usr/bin', '/sbin', '/bin']:
            if item not in path:
                path.append(item)
        path = ':'.join(path)
        env['PATH'] = path
    def run(self, argv): # please do not launch me as a thread
        self.window.set_title(_('Ailurus terminal') + ': ' + ' '.join(argv))
        assert isinstance(argv, list)

        # This idea comes from jhbuild/frontends/gtkui.py
        # I wish to thank Project jhbuild!
        env = os.environ.copy()
        self.populate_path(env) # because PATH of normal user does not contain 'sbin' on Debian
        if Config.get_use_proxy():
            try: 
                proxy_string = get_proxy_string()
                assert proxy_string
            except: pass
            else:
                env.update({'http_proxy':proxy_string,
                            'https_proxy':proxy_string,
                            'ftp_proxy':proxy_string,
                            })
        msg = StringIO.StringIO()
        print >>msg, '\x1b[1;33m' + _('Run command:'), ' '.join(argv), '\x1b[m', '\r'
        self.terminal.feed(msg.getvalue())
        pid = self.terminal.fork_command(command=argv[0], argv=argv,
                                         directory=os.getcwd(),
                                         envv=['%s=%s' % x for x in env.items()],)
        if pid == -1:
            os._exit(1)

if __name__ == '__main__':
    window = Window()
    argv = sys.argv[1:]
    window.run(argv)
    gtk.main()
