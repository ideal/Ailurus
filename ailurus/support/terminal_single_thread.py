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

from lib import *
import sys, os, gtk

class Terminal:
    def read(self, fd):
        r=os.fdopen(fd)
        try:
            while True:
                sys.stdout.flush()
                line = r.readline()
                if len(line)==0: break
                if not gtk: break
                for char in line:
                    if char == '\n': char = '\r\n'
                    self.terminal.feed(char)
        except IOError: pass
        finally:
            try: r.close()
            except: pass
        
    def get_widget(self):
        return self.scrollwindow
    
    def run(self, string):
        import os, shlex, StringIO, gtk
        string = os.path.expandvars(string) 
        argv = shlex.split(string)
        for i,a in enumerate(argv):
            assert type(i)==int
            if a[0]=='~': argv[i]=os.path.expanduser(a)
        print '\x1b[1;33m', _('Run command:'), string, '\x1b[m'
        env = {}
        if Config.get_use_proxy():
            try:
                proxy_string = get_proxy_string()
                assert proxy_string
            except: pass
            else:
                env = os.environ.copy()
                env.update({'http_proxy':proxy_string,
                            'https_proxy':proxy_string,
                            'ftp_proxy':proxy_string,
                            })
        pid = self.terminal.fork_command(command=argv[0],
                                         argv=argv,
                                         directory=os.getcwd(),
                                         envv=['%s=%s' % x for x in env.items()],)
        if pid==-1: raise CommandFailError(string)
        try:
            ret = os.waitpid(pid, 0)[1]
            if ret!=0:
                if ret!=1: # ignore SIGHUP. not a good solution.
                    raise CommandFailError(string, ret)
        except OSError: pass #no such process
    
    def __init__(self):
        import vte, gtk
        self.terminal = terminal = vte.Terminal()
        label = gtk.Label(_('You can press "Ctrl+C" to terminate Ailurus installation process.'))
        align_label = gtk.Alignment(0, 0)
        align_label.add(label)
        align_label.set_border_width(5)
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(align_label, False)
        vbox.pack_start(terminal, True, True)
        # initiate scrolledWindow
        self.scrollwindow = scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(vbox)
