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
import sys, os
from lib import *

class Autostart_Workrave(C):
    __doc__ = _('Automatically start up Workrave')
    detail = _('Create file:') + '~/.config/autostart/workrave.desktop'
    path = os.path.expanduser('~/.config/autostart/')
    file = path + 'workrave.desktop'
    def exists(self):
        if UBUNTU or UBUNTU_DERIV:
            return APT.installed('workrave') and not os.path.exists(self.file)
        if FEDORA:
            return RPM.installed('workrave') and not os.path.exists(self.file)
    def cure(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        with open(self.file, 'w') as f:
            f.write('[Desktop Entry]\n'
                    'Name=Workrave\n'
                    'Exec=workrave\n'
                    'Encoding=UTF-8\n'
                    'Version=1.0\n'
                    'Type=Application\n'
                    'X-GNOME-Autostart-enabled=true\n')

class Create_basic_vimrc(C):
    __doc__ = _('Create basic VIM configuration file (.vimrc)')
    detail = _('File content:') + ' syntax on; set autoindent; set number; set mouse=a'
    file = os.path.expanduser('~/.vimrc')
    def exists(self):
        if UBUNTU or UBUNTU_DERIV:
            return APT.installed('vim') and not os.path.exists(self.file)
        if FEDORA:
            return RPM.installed('vim-enhanced') and not os.path.exists(self.file)
    def cure(self):
        with open(self.file, 'w') as f:
            f.write('syntax on\n'
                    'set autoindent\n'
                    'set number\n'
                    'set mouse=a\n')

class Create_Imagemagick_shortcut(C):
    __doc__ = _('Create ImageMagick shortcut in "Application->Graphics" menu')
    file = '/usr/share/applications/imagemagick.desktop'
    detail = _('Create file:') + ' ' + file
    def exists(self):
        if UBUNTU or UBUNTU_DERIV:
            return APT.installed('imagemagick') and not os.path.exists(self.file)
        if FEDORA:
            return RPM.installed('ImageMagick') and not os.path.exists(self.file)
    def cure(self):
        path = D + 'umut_icons/imagemagick.png'
        run_as_root('cp %s /usr/share/icons/ ' % path)
        create_file(self.file, '[Desktop Entry]\n'
                               'Name=ImageMagick\n'
                               'Exec=display %f\n'    
                               'Encoding=UTF-8\n'
                               'StartupNotify=true\n'
                               'Terminal=false\n'
                               'Type=Application\n'
                               'Categories=GNOME;GTK;Graphics;\n'
                               'Icon=/usr/share/icons/imagemagick.png\n')

class Create_softlink_to_desktop_folder(C):
    __doc__ = _('Create a directory "Desktop" linked to the desktop in your home folder')
    detail = _('After that, you can easily chdir to desktop folder by command "cd ~/Desktop".')
    desktop = os.path.expanduser('~/Desktop')
    def exists(self):
        return not os.path.exists(self.desktop)
    def cure(self):
        with open(os.path.expanduser('~/.config/user-dirs.dirs')) as f:
            contents = f.readlines()
        name = None
        for line in contents:
            if line.startswith('#'): continue
            if 'XDG_DESKTOP_DIR' in line:
                name = line.split('=')[1].strip()
                if name.startswith('"') and name.endswith('"'): name = name[1:-1]
                name = os.path.expandvars(name)
        if name and os.path.exists(name):
            run('ln -s %s %s'%(name, self.desktop))

class Query_before_remove_a_lot_of_files(C) :
    __doc__ = _('Query you before delete more than three files in BASH')
    detail = _('Prevent destruction when you mistype "rm subdir/*" as "rm subdir/ *".\n'
               'Add this line into ~/.bashrc: alias rm="rm -I"')
    bashrc = os.path.expanduser('~/.bashrc')
    line = "alias rm='rm -I'"
    def exists(self):
        return not file_contain(self.bashrc, self.line)
    def cure(self):
        file_append(self.bashrc, self.line)

# This class needs improvement
#
#class Speed_Up_Firefox(I):
#    __doc__ = _('Speed up Firefox')
#    detail = _('Firefox is faster when Pango rendering is disabled. '
#        'The trick is to launch Firefox by the command: "export MOZ_DISABLE_PANGO=1; firefox". '
#        'Ailurus will create a new icon "Firefox without Pango (faster)" in the menu "Applications"-->"Internet".')
#    def install(self):
#        paths = [
#                 '/usr/share/applications/firefox-3.5.desktop',
#                 '/usr/share/applications/firefox.desktop', 
#                 '/usr/share/applications/mozilla-firefox.desktop',
#                 '/usr/share/applications/abrowser.desktop',
#                 ]
#        for path in paths:
#            import os
#            if os.path.exists(path): break
#        else:
#            raise Exception('Firefox shortcut is not found.')
#            
#        with open(path) as f:
#            content = f.readlines()
#        for i, line in enumerate(content):
#            if line.startswith('Exec='):
#                firefox_launcher = line.split('=')[1].strip()
#                new = 'Exec=sh -c "export MOZ_DISABLE_PANGO=1; %s"\n'%firefox_launcher
#                content[i] = new
#            if line.startswith('Name='):
#                content[i] = 'Name=%s\n'%_('Firefox without Pango (faster)')
#        dir = '/usr/local/share/applications/'
#        if not os.path.exists(dir): run_as_root('mkdir ' + dir)
#        with TempOwn(dir + 'firefox.nopango.desktop') as o:
#            with open(dir + 'firefox.nopango.desktop', 'w') as f:
#                f.writelines(content)
#
#    def installed(self):
#        import os 
#        return ( os.path.exists('/usr/local/share/applications/firefox.nopango.desktop') or
#                 os.path.exists('/usr/share/applications/firefox.nopango.desktop') )
#    def remove(self):
#        run_as_root('rm -f /usr/local/share/applications/firefox.nopango.desktop')
#        run_as_root('rm -f /usr/share/applications/firefox.nopango.desktop')

class Show_a_Linux_skill_bubble(C):
    __doc__ = _('Show a random Linux skill after you log in to GNOME')
    detail = _('Create file:') + ' ~/.config/autostart/show-a-linux-skill-bubble.desktop'
    file = os.path.expanduser('~/.config/autostart/show-a-linux-skill-bubble.desktop')
    def exists(self):
        return not os.path.exists(self.file)
    def cure(self):
        with open(self.file, 'w') as f:
            f.write('[Desktop Entry]\n'
                    'Name=Show a random Linux skill after logging in.\n'
                    'Comment=Show a random Linux skill after you log in to GNOME. Help you learn Linux.\n'
                    'Exec=/usr/share/ailurus/support/show-a-linux-skill-bubble\n'
                    'Terminal=false\n'
                    'Type=Application\n'
                    'Icon=' + D + 'suyun_icons/shortcut.png\n'
                    'Categories=System;\n'
                    'StartupNotify=false\n')

class Own_usr_lib_eclipse_by_root(C):
    __doc__ = _('Let root own /usr/lib/eclipse and /usr/share/eclipse')
    detail = _('Otherwise, Pydev and CDT do not work.')
    def wrong(self, path):
        if os.path.exists(path):
            statinfo = os.stat(path)
            if statinfo.st_uid != 0 or statinfo.st_gid != 0:
                return True
        return False
    def exists(self):
        return self.wrong('/usr/lib/eclipse') or self.wrong('/usr/share/eclipse')
    def cure(self):
        run_as_root('chown -R root:root /usr/lib/eclipse', ignore_error=True)
        run_as_root('chown -R root:root /usr/share/eclipse', ignore_error=True)