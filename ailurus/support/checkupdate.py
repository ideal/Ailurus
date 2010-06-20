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
from lib import *
from libu import *

def url_button(url):
    import gtk
    def func(w, url): open_web_page(url)
    def enter(w, e): 
        try: w.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        except AttributeError: pass
    def leave(w, e): 
        try: w.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        except AttributeError: pass
    label = gtk.Label()
    label.set_markup("<span color='blue'><u>%s</u></span>"%url)
    button = gtk.Button()
    button.connect('clicked', func, url)
    button.connect('enter-notify-event', enter)
    button.connect('leave-notify-event', leave)
    button.set_relief(gtk.RELIEF_NONE)
    button.add(label)
    align = gtk.Alignment(0, 0.5)
    align.add(button)
    return align

def version_to_tuple(string):
    return tuple(string.split('.'))

def check_update(silent = False):
    '''Please launch me as a thread
    if silent is true, then do nothing if no new version found.'''
    import gtk, urllib2, re
    if FEDORA:
        pattern1 = r'ailurus-[0-9.]+-.+?'+VERSION+'.+?\.rpm'
        pattern2 = r'ailurus-([0-9.]+)-.+?'+VERSION+'.+?\.rpm'
        url = 'http://homerxing.fedorapeople.org/'
    elif UBUNTU or UBUNTU_DERIV:
        pattern1 = r'ailurus_[0-9.]+-.+?'+VERSION+'.+?\.deb'
        pattern2 = r'ailurus_([0-9.]+)-.+?'+VERSION+'.+?\.deb'
        url = 'http://ppa.launchpad.net/ailurus/ppa/ubuntu/pool/main/a/ailurus/'
    else:
        return
    current_version = AILURUS_VERSION
    try:
        f = urllib2.urlopen(url)
        content = f.read()
        f.close()
    except:
        print_traceback()
        return
    latest_version_tuple = version_to_tuple(current_version)
    for string in re.findall(pattern1, content):
        match = re.match(pattern2, string)
        version = match.group(1)
        tuple = version_to_tuple(version)
        if tuple > latest_version_tuple:
            latest_version_tuple = tuple
            latest_filename = string
    
    latest_version = '.'.join(list(latest_version_tuple))
    dlg = gtk.Dialog('',
                     None, gtk.DIALOG_NO_SEPARATOR,
                     (gtk.STOCK_CLOSE, gtk.RESPONSE_OK))
    vbox = gtk.VBox(False, 5)
    if latest_version != current_version:
        dlg.set_title(_('New version available'))
        label = gtk.Label(_('Version %s released!') % latest_version)
        button = url_button(url + latest_filename)
        vbox.pack_start(label)
        vbox.pack_start(button, False)
    else:
        dlg.set_title(_('Check update'))
        label = gtk.Label( _('You are using the latest Ailurus :)') )
        vbox.pack_start(label)
    image = gtk.Image()
    image.set_from_file(D+'suyun_icons/update.png')
    hbox = gtk.HBox(False, 5)
    hbox.pack_start(image, False)
    hbox.pack_start(vbox, False)
    dlg.vbox.pack_start(hbox, False)
    dlg.vbox.show_all()
    if not silent or latest_version != current_version:
        gtk.gdk.threads_enter()
        dlg.run()
        dlg.destroy()
        gtk.gdk.threads_leave()

def show_about_dialog():
    import gtk
    gtk.about_dialog_set_url_hook( lambda dialog, link: 1 )
    about = gtk.AboutDialog()
    about.set_logo(gtk.gdk.pixbuf_new_from_file(D+'suyun_icons/logo.png'))
    about.set_name('Ailurus')
    about.set_version(AILURUS_VERSION)
    about.set_website_label( _('Project homepage') )
    about.set_website('http://ailurus.googlecode.com/')
    about.set_authors( [
          _('Developers:'),
          'Homer Xing <homer.xing@gmail.com>', 
          'CHEN Yangyang <skabyy@gmail.com>',
          'MA Yue <velly.empire@gmail.com>',
          'QI Chengjie <starboy.qi@gmail.com>',
          'HAN Haofu <gtxx3600@gmail.com>',
          _('Contributors:'),
          'HUANG Wei <wei.kukey@gmail.com>',
          'SHANG Yuanchun <idealities@gmail.com>',
          'DU Yue <elyes.du@gmail.com>',
          'Devil Wang <wxjeacen@gmail.com>',
          'Ray Chen <chenrano2002@gmail.com>',
           ] )
    about.set_translator_credits(_('translator-credits'))
    about.set_artists( [
          'SU Yun',
          'M. Umut Pulat    http://12m3.deviantart.com/', 
          'Andrea Soragna   http://sora-meliae.deviantart.com/',
          'Paul Davey       http://mattahan.deviantart.com/',] )
    about.set_copyright( _(u"Copyright © 2007-2010,\nTrusted Digital Technology Laboratory,\nShanghai Jiao Tong University, China.") + '\n'
                         + _(u"Copyright © 2009-2010, Ailurus Developers Team") )
    about.set_wrap_license(False)
    about.set_license('''
Ailurus is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

The source code in Ailurus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Ailurus; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

All images in directory "data/suyun_icons" are released under the GPL License.
Their copyright are holded by SU Yun.

All images in directory "data/umut_icons" are released under the GNU Lesser General Public License.
Their copyright are holded by M. Umut Pulat.

All images in directory "data/sona_icons" are released under the GPL License. 
Their copyright are holded by Andrea Soragna.

All images in directory "data/velly_icons" are released under the GPL License. 
Their copyright are holded by MA Yue.''')
    about.vbox.pack_start( gtk.Label( _('\nThis version is released at %s.') % AILURUS_RELEASE_DATE), False)
    about.vbox.show_all()
    about.run()
    about.destroy()

def show_special_thank_dialog():
    import StringIO
    text = StringIO.StringIO()
    print >>text, _('We wish to express thankfulness to these projects:')
    print >>text, '<b><big>Lazybuntu, UbuntuAssistant'
    print >>text, 'GTweakUI, Easy Life, Ubuntu-tweak, CPU-G</big></b>'
    print >>text
    print >>text, _('We sincerely thank these people:')
    print >>text
    print >>text, _('The people who provide inspiration:')
    print >>text, '<b><big>PCMan, Careone, novia, '
    print >>text, 'BAI Qingjie, Aron Xu, Federico Vera, '
    print >>text, 'ZHU Jiandy, Maksim Lagoshin, '
    print >>text, 'Romeo-Adrian Cioaba, David Morre, '
    print >>text, 'Liang Suilong, Lovenemesis, Chen Lei, '
    print >>text, 'DaringSoule, Ramesh Mandaleeka, JCOM, '
    print >>text, 'Michael McBride</big></b>'
    print >>text
    print >>text, _('The people who designs the logo:')
    print >>text, '<b><big>SU Yun</big></b>'
    print >>text
    print >>text, _('The people who maintain PPA repository:')
    print >>text, '<b><big>Aron Xu</big></b>'
    print >>text
    print >>text, _('The people who provide a lot of Linux skills:')
    print >>text, '<b><big>Oneleaf</big></b>'
    print >>text
    print >>text, _('The people who provide a lot of Debian packages:')
    print >>text, '<b><big>Careone</big></b>'
    print >>text
    print >>text, _('The people who provide a lot of translation:')
    print >>text, '<b><big>Federico Vera, Sergey Sedov, Sérgio Marques</big></b>', 
    print >>text, _('and many other people.')
    print >>text 
    print >>text, _('The people who report bugs:')
    print >>text, '<b><big>LIU Liang, YU Pengfei, q1ha0,'
    print >>text, 'novia, hardtzh, fegue</big></b>', _('and many other people.')
    print >>text
    print >>text, _('The people who eliminate bugs:')
    print >>text, '<b><big>anjiannian, PES6, eemil.lagerspetz</big></b>'
    print >>text
    print >>text, _('The people who publicize this software:')
    print >>text, '<b><big>dsj, BingZhiGuFeng, chinairaq, coloos,'
    print >>text, 'TombDigger, sudo, Jandy Zhu</big></b>', _('and many other people.')
    print >>text
    print >>text, _('and the people not mensioned here.')
    import gtk
    label = gtk.Label()
    label.set_markup(text.getvalue())
    text.close()
    label.set_justify(gtk.JUSTIFY_CENTER)
    scroll = gtk.ScrolledWindow()
    scroll.add_with_viewport(label)
    scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    scroll.set_shadow_type(gtk.SHADOW_NONE)
    scroll.set_size_request(-1, 500)
    dialog = gtk.Dialog( _('Thanks'), None, 
        gtk.DIALOG_MODAL | 
        gtk.DIALOG_NO_SEPARATOR, 
        buttons = (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
    dialog.set_border_width(10)
    dialog.vbox.pack_start(scroll, False, False)
    dialog.vbox.show_all()
    dialog.run()
    dialog.destroy()

def show_changelog():
    with open('/usr/share/ailurus/ChangeLog') as f:
        lines = f.readlines()
    import gtk, pango, re
    buffer = gtk.TextBuffer()
    buffer.create_tag('feature', font='DejaVu Serif')
    buffer.create_tag('date', scale=pango.SCALE_SMALL, foreground='purple')
    buffer.create_tag('contributor', weight=pango.WEIGHT_BOLD)
    buffer.create_tag('email', scale=pango.SCALE_SMALL, foreground='blue')
    pattern = re.compile(r'(\S+) ([^<]+)(<[^>]+>)')
    end = buffer.get_end_iter()
    for line in lines:
        if line.strip() == '': # do not display blank line
            pass
        elif line.startswith('2'): # this is a line consists of date, contributor, email
            match = pattern.match(line)
            if not match:
                print 'not match:', line
            else:
                date = match.group(1)
                contributor = match.group(2).strip()
                email = match.group(3)
                buffer.insert_with_tags_by_name(end, date, 'date')
                buffer.insert(end, ' ')
                buffer.insert_with_tags_by_name(end, contributor, 'contributor')
                buffer.insert(end, ' ')
                buffer.insert_with_tags_by_name(end, email, 'email')
                buffer.insert(end, '\n')
        elif line.startswith('\t') or line.startswith(' '): # this is a line of feature description
            buffer.insert_with_tags_by_name(end, line, 'feature')
    textview = gtk.TextView()
    textview.set_buffer(buffer)
    textview.set_editable(False)
    textview.set_cursor_visible(False)
    textview.set_wrap_mode(gtk.WRAP_WORD)
    gray_bg(textview)
    scroll = gtk.ScrolledWindow()
    scroll.add(textview)
    scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    scroll.set_shadow_type(gtk.SHADOW_IN)
    close_button = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
    close_button.connect('clicked', lambda *w: window.destroy())
    buttonbox = gtk.HBox(False, 10)
    buttonbox.pack_end(close_button, False)
    vbox = gtk.VBox(False, 10)
    vbox.pack_start(scroll)
    vbox.pack_start(buttonbox, False)

    window = gtk.Window()
    window.set_title(_('Ailurus changelog'))
    window.add(vbox)
    window.set_default_size(600, 400)
    window.set_border_width(10)
    window.set_position(gtk.WIN_POS_CENTER)
    window.show_all()
