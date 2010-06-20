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

from lib import *
import gtk

class Terminal:
    def read(self, fd):
        import os, gtk
        r=os.fdopen(fd)
        try:
            while True:
                line = r.readline()
                if len(line)==0: break
                if not gtk: break
                gtk.gdk.threads_enter()
                for char in line:
                    if char == '\n': char = '\r\n'
                    self.terminal.feed(char)
                gtk.gdk.threads_leave()
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
        
        # This idea comes from jhbuild/frontends/gtkui.py
        # I wish to thank Project jhbuild!
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
        msg = StringIO.StringIO()
        print >>msg, '\x1b[1;33m', _('Run command:'), string, '\x1b[m', '\r'
        gtk.gdk.threads_enter()
        self.terminal.feed(msg.getvalue())
        pid = self.terminal.fork_command(command=argv[0],
                                         argv=argv,
                                         directory=os.getcwd(),
                                         envv=['%s=%s' % x for x in env.items()],)
        gtk.gdk.threads_leave()
        if pid==-1: raise CommandFailError(string)
        try:
            ret = os.waitpid(pid, 0)[1]
            if ret: raise CommandFailError(string, ret)
        except OSError: pass #no such process
    
    def __init__(self):
        import os, sys, vte, gtk, thread
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
        self.stdout_origin = os.dup(sys.stdout.fileno())
        self.r, self.w = os.pipe()
        thread.start_new_thread(self.read, (self.r,) )
    
    def redirect_stdout(self):
        import os, sys
        os.dup2(self.w, sys.stdout.fileno())
    
    def recover_stdout(self):
        import os, sys
        os.dup2(self.stdout_origin, sys.stdout.fileno())