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
import sys, os
from libapp import *
from lib import *

class ChangeTerminalColor(_set_gconf):
    __doc__ = _('Change background color of GNOME terminal to black.')
    detail = _('Set background color to black. Set foreground color to white.\n'
       'The trick is to change GConf values:\n'
       '/apps/gnome-terminal/profiles/Default/use_theme_colors = False\n'
       '/apps/gnome-terminal/profiles/Default/background_color = #000000000000\n'
       '/apps/gnome-terminal/profiles/Default/foreground_color = #FFFFFFFFFFFF')
    DE = 'gnome'
    def __init__(self):
        self.set=(
('/apps/gnome-terminal/profiles/Default/use_theme_colors',False,True), 
('/apps/gnome-terminal/profiles/Default/background_color','#000000000000','#FFFFFFFFFFFF'), 
('/apps/gnome-terminal/profiles/Default/foreground_color','#FFFFFFFFFFFF','#000000000000'),
                  )
        self.add=()

class NScripts(I):
    __doc__ = _('NScripts: a set of useful Nautilus scripts')
    detail = _('NScripts help you change the background, create/check MD5 checksums, create a diff, create shortcuts via Nautilus.\n'
               'NScripts is installed in $HOME/.gnome2/nautilus-scripts.')
    download_url = 'http://freshmeat.net/projects/nscripts'
    license = GPL
    category = 'nautilus_extension'
    DE = 'gnome'
    def install(self):
        # We add the first url in case of failure of the second one 
        f = R(['http://ailurus.googlecode.com/files/NScripts-3.6.tar.bz2', urls.nscript]).download()
        import os
        dir = os.path.expanduser('~/.gnome2/nautilus-scripts/')
        if not os.path.exists(dir): os.mkdir(dir)
        with Chdir('/tmp'):
            os.system('tar xf ' + f)
            os.system('cp -r nscripts/* ' + dir)
            os.remove(dir + 'ChangeLog')
            os.remove(dir + 'TODO')
            os.system('touch ' + dir +'.nscripts_is_installed')

    def installed(self):
        import os
        d = os.path.expanduser('~/.gnome2/nautilus-scripts/.nscripts_is_installed')
        return os.path.exists(d)

    def remove(self):
        for dir in ['Admin', 'Files', 'Root', 'Utils']:
            run('rm -rf $HOME/.gnome2/nautilus-scripts/' + dir)
        run('rm $HOME/.gnome2/nautilus-scripts/.nscripts_is_installed')

class Gedit_GB2312(_set_gconf) :
    __doc__ = _('Add GB2312 detection ability to GEdit')
    detail = _('The trick behind is to change GConf values:\n'
       '/apps/gedit-2/preferences/encodings/auto_detected += ["GB2312", "GBK", "GB18030"]\n'
       '/apps/gedit-2/preferences/encodings/shown_in_menu += ["GB2312"]')
    Chinese = True
    DE = 'gnome'
    def __init__(self):
        self.set = ()
        self.add = (
('/apps/gedit-2/preferences/encodings/auto_detected', [ 'GB2312', 'GBK', 'GB18030' ] ),
('/apps/gedit-2/preferences/encodings/shown_in_menu', [ 'GB2312' ] ),
                    )

class Speedup_Nautilus(I):
    __doc__ = _('Speed up Nautilus')
    detail = _('Change Nautilus settings: '
       'Do not count directory items. Do not preview sound. '
       'Do not show texts in icon. Use tighter layout. \n'
       'The trick behind is to change GConf settings as follows.\n'
       '/apps/nautilus/preferences/show_directory_item_counts = never\n'
       '/apps/nautilus/preferences/preview_sound = never\n'
       '/apps/nautilus/preferences/show_icon_text = never\n'
       '/apps/nautilus/icon_view/default_use_tighter_layout = true\n'
       'delete "size" from /apps/nautilus/list_view/default_visible_columns')
    category = 'nautilus_extension'
    DE = 'gnome'
    
    def __init__(self):
        self.keys = ['/apps/nautilus/preferences/show_icon_text',
                     '/apps/nautilus/preferences/show_directory_item_counts',
                     '/apps/nautilus/preferences/preview_sound']
        self.key1 = '/apps/nautilus/icon_view/default_use_tighter_layout'
        self.key2 = '/apps/nautilus/list_view/default_visible_columns'
        
    def install(self):
        import gconf
        g = gconf.client_get_default()
        for key in self.keys:
            g.set_string(key, 'never')
        g.set_bool(self.key1, True)
        value = g.get_list(self.key2, gconf.VALUE_STRING)
        if 'size' in value:
            value.remove('size')
        g.set_list(self.key2, gconf.VALUE_STRING, value)

    def remove(self):
        import gconf
        g = gconf.client_get_default()
        for key in self.keys:
            g.set_string(key, 'local_only')
        g.set_bool(self.key1, False)
        value = g.get_list(self.key2, gconf.VALUE_STRING)
        if 'size' not in value:
            value.insert(1, 'size')
        g.set_list(self.key2, gconf.VALUE_STRING, value)

    def installed(self):
        import gconf
        g = gconf.client_get_default()
        value = g.get_list(self.key2, gconf.VALUE_STRING)
        if ( 'size' in value or
             g.get_bool(self.key1) == False or
             g.get_string(self.keys[0]) != 'never' or
             g.get_string(self.keys[1]) != 'never' or
             g.get_string(self.keys[2]) != 'never' ):
            return False
        else:
            return True

class GEdit_Suitable_For_Programmer(_set_gconf):
    __doc__ = _('Make GEdit more suitable for programmers')
    detail = _('Change GEdit settings as follows:\n'
       'Automatically indent current line. '
       'Do not automatically create a hidden copy of current file. '
       'Automatically save files once in each minute. '
       'Show line numbers.')
    category = 'saber'
    DE = 'gnome'
    def __init__(self):
        self.set = (
('/apps/gedit-2/preferences/editor/save/auto_save',True,False),
('/apps/gedit-2/preferences/editor/save/auto_save_interval',1,10),
('/apps/gedit-2/preferences/editor/save/create_backup_copy',False,True),
('/apps/gedit-2/preferences/editor/line_numbers/display_line_numbers',True,False),
('/apps/gedit-2/preferences/editor/auto_indent/auto_indent',True,False),
                    )
        self.add = ()

