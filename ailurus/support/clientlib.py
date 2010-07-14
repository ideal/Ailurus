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

import urllib
import urllib2

import gtk
import pango

from lib import *
from libu import *

LOCAL_DEBUG = 0
if LOCAL_DEBUG:
    HOST = 'localhost'
    PORT = 8080
else:
    HOST = 'we-like-ailurus.appspot.com'
    PORT = 80
    
delayed = []

def load_delayed_data():
    import os
    import pickle
    fn = os.path.expanduser('~/.config/ailurus/delayed_sending')
    try:
        with open(fn, 'r') as f:
            global delayed
            delayed = pickle.load(f)
    except:
        pass

def save_delayed_data():
    import os
    import pickle
    fn = os.path.expanduser('~/.config/ailurus/delayed_sending')
    try:
        with open(fn, 'w') as f:
            pickle.dump(delayed, f)
    except:
        import traceback, sys
        traceback.print_exc(file=sys.stderr)

def __do_try_send_delayed_data():
    load_delayed_data()
    i = 0
    while i < len(delayed):
        try:
            req = delayed[i]
            req[0](*req[1:])
            delayed.remove(req)
        except urllib2.URLError:
            i += 1
            pass
#            import traceback, sys
#            traceback.print_exc(file=sys.stderr)
    save_delayed_data()

def try_send_delayed_data():
    __do_try_send_delayed_data()

def send(d, host, port):
    assert type(d) == dict
    url = 'http://%s:%d/sign' % (host, port)
    data = urllib.urlencode(d)
    req = urllib2.Request(url, data)
    urllib2.urlopen(req).close()

def skill_send(user, content, host=HOST, port=PORT):
    d = {'user': user,
         'type': 'skill',
         'content': content,
         }
    send(d, host, port)

def suggestion_send(user, content, host=HOST, port=PORT):
    d = {'user': user,
         'type': 'suggestion',
         'content': content,
         }
    send(d, host, port)

class SubmitWindow(gtk.Window):
    def __init__(self, title, submit_method):
        self.submit = submit_method
        gtk.Window.__init__(self)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title(title)
        self.set_border_width(5)
        self.set_size_request(300, 400)
        
        self.nameentry = nameentry = gtk.Entry()
        nameentry.set_text(Config.get_username_of_suggestion_window())

        namebox = gtk.HBox(False, 5)
        namebox.pack_start(gtk.Label(_('Your name:')), False)
        namebox.pack_start(nameentry)
        
        contentbox = gtk.HBox()
        self.textview = textview = gtk.TextView()
        textview.modify_font(pango.FontDescription('Monospace 10'))
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroll.add(textview)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        contentbox.pack_start(scroll, True)
        
        buttonbox = gtk.HBox(False, 10)
        submitbtn = image_stock_button(gtk.STOCK_APPLY, _('Submit'))
        submitbtn.connect('clicked', self.__submit, 
                          nameentry, 
                          textview)
        cancelbtn = image_stock_button(gtk.STOCK_CANCEL, _('Cancel'))
        cancelbtn.connect('clicked', self.__cancel)
        buttonbox.pack_end(submitbtn, False)
        buttonbox.pack_end(cancelbtn, False)
        
        vbox = gtk.VBox(False, 10)
        vbox.pack_start(namebox, False)
        vbox.pack_start(contentbox, True)
        vbox.pack_end(buttonbox, False)
        self.add(vbox)
        self.show_all()
    
    def __quit(self):
        self.destroy()
    
    def __submit(self, btn, nameentry, textview):
        name = nameentry.get_text()
        buffer = textview.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), 
                               buffer.get_end_iter())
        try:
            self.submit(name, text)
        except urllib2.HTTPError:
            import traceback
            import sys
            traceback.print_exc(file=sys.stderr)
            dlg = gtk.MessageDialog(self, 0,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  _('HTTP error'),
                                  )
            dlg.run()
            dlg.destroy()
        except urllib2.URLError:
            dlg = gtk.MessageDialog(self, 0,
                                  gtk.MESSAGE_QUESTION,
                                  gtk.BUTTONS_YES_NO,
                                  _('Can not connect to server.\n'
                                    'Would you like to save the request and resend when next time ailurus starts?'),
                                  )
            to_be_saved = dlg.run()
            if to_be_saved:
                delayed.append((self.submit, name, text))
                save_delayed_data()
            dlg.destroy()
        self.__quit()
    
    def __cancel(self, btn):
        self.__quit()

class SkillsSubmit(SubmitWindow):
    def __init__(self):
        SubmitWindow.__init__(self, _('Submit a Linux skill'), skill_send)

class SuggestionsSubmit(SubmitWindow):
    def __init__(self):
        SubmitWindow.__init__(self, _('Propose suggestion'), suggestion_send)

if __name__ == '__main__':
    skill_send('bb', 'test skill')
    print 'OK'
    print urllib2.urlopen('http://%s:%d/' % (HOST, PORT)).read()
