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
from lib import *
import urls

__all__ = ['_set_gconf', '_apt_install', '_path_lists', 
           '_ff_extension', '_download_one_file', '_rpm_install', 'N',
           'create_eclipse_icon', 'install_eclipse_extension_message',
           'remove_eclipse_extesion_message', 'latest', 'urls']

class _set_gconf(I):
    'Must subclass me and set "self.set" and "self.add"'
    DE = 'gnome'
    def __check_key(self, key):
        if key=='':
            raise ValueError
        import re
        if re.match(r'^(/[a-zA-Z0-9-_]+)+$',key) is None:
            raise ValueError
    def __check_list(self, List):
        if len(List)==0:
            raise ValueError
        for e in List:
            if type(e)!=str:
                raise ValueError
            if e=='':
                raise ValueError
    def self_check(self):
        self.set # check existing
        self.add # check existing
        if type(self.set)!=tuple or type(self.add)!=tuple:
            raise TypeError
        for e in self.set:
            if type(e)!=tuple:
                raise TypeError
            if len(e)!=3:
                raise TypeError
            if type(e[0])!=str:
                raise TypeError
            self.__check_key(e[0])
            if type(e[1])!=bool and type(e[1])!=int and type(e[1])!=float and type(e[1])!=str:
                raise TypeError
            if type(e[2])!=bool and type(e[2])!=int and type(e[2])!=float and type(e[2])!=str:
                raise TypeError
        for e in self.add:
            if type(e)!=tuple:
                raise TypeError
            if len(e)!=2:
                raise TypeError
            if type(e[0])!=str:
                raise TypeError
            self.__check_key(e[0])
            if type(e[1])!=list:
                raise TypeError
            self.__check_list(e[1])
    def __init__(self):
        raise NotImplementedError
    def install(self):
        import gconf
        G = gconf.client_get_default()
        if len(self.set) or len(self.add):
            print '\x1b[1;32m', _("Change GConf values:"), '\x1b[m'
        for key, newvalue, oldvalue in self.set:
            G.set_value(key, newvalue)
            print "\x1b[1;32m%s\x1b[m"%_("Key:"), key,
            print "\x1b[1;32m%s\x1b[m"%_("New value:"), newvalue
        for key, to_add_list in self.add:
            List = G.get_list(key, gconf.VALUE_STRING)
            for to_add in to_add_list:
                try:
                    List.remove(to_add)
                except ValueError:
                    pass
                List.insert(0, to_add)
            G.set_list(key, gconf.VALUE_STRING, List)
            print "\x1b[1;32m%s\x1b[m"%_("Key:"), key
            print "\x1b[1;32m%s\x1b[m"%_("Appended items:"), to_add_list
    def installed(self):
        import gconf
        G = gconf.client_get_default()
        for key, newvalue, oldvalue in self.set:
            try:
                value=G.get_value(key)
                if type(value)!=float and value!=newvalue:
                    return False
                if type(value)==float and  abs(value-newvalue)>1e-6:
                    return False
            except ValueError: #key does not exist
                return False
        for key, to_add_list in self.add:
            List = G.get_list(key, gconf.VALUE_STRING)
            for to_add in to_add_list:
                if not to_add in List:
                    return False
        return True
    def remove(self):
        import gconf
        G = gconf.client_get_default()
        if len(self.set) or len(self.add):
            print '\x1b[1;31m', _("Change GConf values:"), '\x1b[m'
        for key, newvalue, oldvalue in self.set:
            G.set_value(key, oldvalue)
            print "\x1b[1;31m%s\x1b[m"%_("Key:"), key,
            print "\x1b[1;31m%s\x1b[m"%_("New value:"), oldvalue
        for key, to_remove_list in self.add:
            List = G.get_list(key, gconf.VALUE_STRING)
            for to_remove in to_remove_list:
                try:
                    List.remove(to_remove)
                except ValueError:
                    pass
            G.set_list(key, gconf.VALUE_STRING, List)
            print "\x1b[1;31m%s\x1b[m"%_("Key:"), key
            print "\x1b[1;31m%s\x1b[m"%_("Removed items:"), to_remove_list
    def visible(self):
        try:
            import gconf
            return True
        except:
            return False 

def is_package_names_string(string):
    assert isinstance(string, str)
    if string == '':
        raise ValueError, 'String is empty.'
    for pkg in string.split():
        import re
        if re.match(r'^[a-zA-Z0-9._+-]+$', pkg) is None:
            raise ValueError, pkg
        if pkg[0]=='-':
            raise ValueError, pkg

def debian_installation_command(package_names):
    return 'apt-get install ' + package_names

def fedora_installation_command(package_names):
    return 'yum install ' + package_names

def archlinux_installation_command(package_names):
    return 'pacman -S ' + package_names

def ppa_to_deb_conf(ppa_string):
    'return deb conf string from ppa string'
    ppa_owner = ppa_string.split("/")[0]
    try: ppa_name = ppa_string.split("/")[1]
    except IndexError: ppa_name = "ppa"
    return "deb http://ppa.launchpad.net/%s/%s/ubuntu %s main" % (ppa_owner, ppa_name, VERSION)

class _apt_install(I):
    deb = '' # deb conf string. It will be written to /etc/apt/sources.list
    ppa = '' # ppa string. If it is not empty, then set self.deb = ppa_to_deb_conf(self.ppa)
    'Must subclass me and set "pkgs".'
    def self_check(self):
        is_package_names_string(self.pkgs)
        if self.ppa: self.deb = ppa_to_deb_conf(self.ppa)
    def install(self):
        APT.install(*self.pkgs.split())
    def installed(self):
        for pkg in self.pkgs.split():
            if not APT.installed ( pkg ):
                return False
        return True
    def get_reason(self, f):
        all_pkgs = self.pkgs.split()
        if len(all_pkgs) > 1:
            not_installed = [p for p in all_pkgs if not APT.installed(p)]
            if len(not_installed) != len(all_pkgs):
                print >>f, _('Because the packages "%s" are not installed.')%' '.join(not_installed),
    def remove(self):
        APT.remove(*self.pkgs.split() )
    def fill(self):
        command = debian_installation_command(self.pkgs)
        if self.ppa:
            self.how_to_install = 'add-apt-repository ppa:%s; %s' % (self.ppa, command)
        elif self.deb:
            self.how_to_install = _('Add source "<b>%s</b>"; %s') % (self.deb, command)
        else:
            self.how_to_install = command
    def add_temp_repository(self):
        if self.deb:
            with TempOwn('/etc/apt/sources.list.d/temp.list'):
                with open('/etc/apt/sources.list.d/temp.list', 'a') as f:
                    print >>f, self.deb
            APT.neet_to_run_apt_get_update()
    def clean_temp_repository(self):
        if os.path.exists('/etc/apt/sources.list.d/temp.list'):
            run_as_root('rm -f /etc/apt/sources.list.d/temp.list')

class _rpm_install(I):
    def self_check(self):
        is_package_names_string(self.pkgs)
    def install(self):
        RPM.install(*self.pkgs.split())
    def installed(self):
        for p in self.pkgs.split():
            if not RPM.installed(p): return False
        return True
    def remove(self):
        RPM.remove(*self.pkgs.split())
    def get_reason(self, f):
        all_pkgs = self.pkgs.split()
        if len(all_pkgs) > 1:
            not_installed = [p for p in all_pkgs if not RPM.installed(p)]
            if len(not_installed) != len(all_pkgs):
                print >>f, _('Because the packages "%s" are not installed.')%' '.join(not_installed),
    def fill(self):
        self.how_to_install = fedora_installation_command(self.pkgs)
    def add_temp_repository(self):
        # FIXME: should write repository configuration to temp file
        if hasattr(self, 'depends'):
            self.depends.install()
    def clean_temp_repository(self):
        # FIXME
        if hasattr(self, 'depends'):
            self.depends.remove()

class _pacman_install(I):
    def self_check(self):
        is_package_names_string(self.pkgs)
    def install(self):
        PACMAN.install(*self.pkgs.split())
    def installed(self):
        for pkg in self.pkgs.split():
            if not PACMAN.installed (pkg):
                return False
        return True
    def get_reason(self, f):
        all_pkgs = self.pkgs.split()
        if len(all_pkgs) > 1:
            not_installed = [p for p in all_pkgs if not PACMAN.installed(p)]
            if len(not_installed) != len(all_pkgs):
                print >>f, _('Because the packages "%s" are not installed.')%' '.join(not_installed),
    def remove(self):
        PACMAN.remove(*self.pkgs.split())
    def fill(self):
        self.how_to_install = archlinux_installation_command(self.pkgs)

class N(I):
    def self_check(self):
        if hasattr(self, 'pkgs'):
            is_package_names_string(self.pkgs)
    def install(self):
        self.backend.install(*self.pkgs.split())
    def installed(self):
        for p in self.pkgs.split():
            if not self.backend.installed(p): return False
        return True
    def remove(self):
        self.backend.remove(*self.pkgs.split())
    def get_reason(self, f):
        all_pkgs = self.pkgs.split()
        if len(all_pkgs) > 1:
            not_installed = [p for p in all_pkgs if not self.backend.installed(p)]
            if len(not_installed) != len(all_pkgs):
                print >>f, _('Because the packages "%s" are not installed.')%' '.join(not_installed),
    def fill(self):
        self.how_to_install = self.installation_command_backend(self.pkgs)
    def visible(self):
        if not hasattr(self, 'pkgs'): 
            #print self.__doc__, ' is hidden because no package name.'
            return False # It is not supported for this Linux distribution.
        # package names change from time to time. we hide an item if package_name does not exists. 
        for pkg in self.pkgs.split():
            if not self.backend.exist(pkg):
                print self.__doc__, ' is hidden because package name changed.'
                return False
        return True

    if FEDORA:
        backend = RPM
        installation_command_backend = staticmethod(fedora_installation_command)
    elif UBUNTU or UBUNTU_DERIV:
        backend = APT
        installation_command_backend = staticmethod(debian_installation_command)
    elif ARCHLINUX:
        backend = PACMAN
        installation_command_backend = staticmethod(archlinux_installation_command)

class _path_lists(I):
    def self_check(self):
        if not isinstance(self.paths, list):
            raise TypeError
        if len(self.paths)==0: 
            raise ValueError
        for path in self.paths:
            if not isinstance(path, str):
                raise TypeError
            if path=='':
                raise ValueError
    def install(self):
        raise NotImplementedError
    def installed(self):
        for path in self.paths:
            import os
            if not os.path.exists(path):
                return False
        return True
    def remove(self):
        for path in self.paths:
            run_as_root('rm "%s" -rf'%path)
    def get_reason(self, f):
        import os
        not_exist = [p for p in self.paths if not os.path.exists(p)]
        if not_exist:
            print >>f, _('Because "%s" does not exist.')%' '.join(not_exist),

def latest(id): # used in all subclasses of _ff_extension, to construct download url. id is the number of firefox extension.
    return 'https://addons.mozilla.org/en-US/firefox/downloads/latest/%s' % id

class _ff_extension(I):
    'Firefox Extension'
    category = 'firefox_extension'
    sane = False # FIXME: we don't know how to remove Firefox extensions
    def self_check(self):
        assert self.name
        assert isinstance(self.name, unicode)
        assert self.R
        assert isinstance(self.R, R)
        assert self.R.filename.endswith('.xpi') or self.R.filename.endswith('.jar')
        assert isinstance(self.download_url, str) and self.download_url
    def install(self):
        f = self.R.download()
        firefox.install_extension_archive(f)
        delay_notify_firefox_restart()
    def installed(self):
        return firefox.extension_archive_exists(self.R.filename) or firefox.extension_is_installed(self.name)
    def remove(self):
        if firefox.extension_archive_exists(self.R.filename):
            firefox.remove_extension_archive(self.R.filename)
        else:
            print '\x1b[1;31m', _("This extension cannot be removed by Ailurus. It can be removed in 'Tools'->'Add-ons' menu of firefox."), '\x1b[m'
    def visible(self):
        return firefox.support

class _download_one_file(I):
    def install(self):
        assert isinstance(self.R, R)
        f = self.R.download()
        run('cp "%s" "%s"' % (f, self.file))
    def installed(self):
        import os
        return os.path.exists(self.file)
    def remove(self):
        run('''rm -f '%s' '''%self.file)
    def get_reason(self, f):
        import os
        if not os.path.exists(self.file):
            print >>f, _('Because "%s" does not exist.')%self.file,

def create_eclipse_icon():
    memarg = ''
    try:
        f = open('/proc/meminfo')
        for line in f:
            if 'MemTotal' in line:
                amount = int(line.split()[1]) ; break
        if amount >= 1024 * 1024 * 1.5:
            memarg = '-Xms512M -Xmx1024M'
    except:
        pass
    icon = '/usr/share/applications/eclipse.desktop'
    with TempOwn(icon):
        with open(icon, 'w') as f:
            f.write('''[Desktop Entry]
Name=Eclipse
Exec=sh -c "export GDK_NATIVE_WINDOWS=true; exec /usr/lib/eclipse -vmargs ''' + memarg + ''' -Dsun.java2d.opengl=true"
Encoding=UTF-8
StartupNotify=true
Terminal=false
Type=Application
Categories=Development
Icon=/usr/lib/eclipse/icon.xpm''')

def install_eclipse_extension_message(title, content):
    import StringIO
    assert isinstance(title, (str, unicode)) and title
    assert isinstance(content, (str, unicode, StringIO.StringIO) )
    if isinstance(content, StringIO.StringIO): content = content.getvalue()
    import gtk
    dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_CLOSE)
    dialog.set_title( _('Installing Eclipse extension') )
    dialog.set_markup('<big><b>%s</b></big>\n\n'%title + content)
    dialog.show_all()
    gtk.gdk.threads_enter()
    dialog.run()
    dialog.destroy()
    gtk.gdk.threads_leave()

def remove_eclipse_extesion_message(name):
    assert isinstance(name, (str, unicode)) and name
    title = _('Removing %s') % name
    import StringIO
    msg = StringIO.StringIO()
    print >>msg, _('Please launch Eclipse, and go to "Help" -> "About Eclipse SDK".')
    print >>msg
    print >>msg, _('Click the "Installation Details" button. Then remove %s.') % name
    import gtk
    label = gtk.Label(msg.getvalue())
    close = gtk.Button(stock = gtk.STOCK_CLOSE)
    close.connect('clicked', lambda w: window.destroy())
    align = gtk.Alignment(1, 0.5)
    align.add(close)
    box = gtk.VBox(False)
    box.pack_start(label, False)
    box.pack_start(align, False)
    window = gtk.Window()
    window.set_title(title)
    window.add(box)
    window.set_border_width(10)
    window.set_position(gtk.WIN_POS_CENTER)
    window.show_all()
