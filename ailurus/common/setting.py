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
import gtk
import sys, os
from lib import *
from libu import *
from libsetting import *

def __change_kernel_swappiness():
    vbox = gtk.VBox()
    text_box = gtk.HBox(False)
    text_box.pack_start( gtk.Label( _('0 = Swap little mem to disk') ), False, False )
    text_box.pack_start( gtk.Label(), True, True, 30 )
    text_box.pack_start( gtk.Label( _('100 = Swap a lot of mem to disk') ), False, False )
    
    current_value = int( get_output('/sbin/sysctl -n vm.swappiness').strip() )
    adjustment = gtk.Adjustment(current_value, 0, 100, 10, 10, 0)
    def update(adjustment):
        new_value = round( adjustment.value, -1 )
        adjustment.set_value( new_value )
    adjustment.connect("value_changed", update)
    scale = gtk.HScale(adjustment)
    scale.set_digits(0)
    scale.set_value_pos(gtk.POS_BOTTOM)

    def apply(w, adjustment):
        new_value = int( adjustment.get_value() )
        new_line = 'vm.swappiness = %s' % new_value
        with TempOwn('/etc/sysctl.conf') as o:
            with open('/etc/sysctl.conf') as f:
                contents = f.readlines()
            for i, line in enumerate(contents):
                if line[0]=='#' or line=='\n': continue
                if 'vm.swappiness' in line:
                    contents[i] = new_line
                    break
            else:
                contents.append(new_line)
            with open('/etc/sysctl.conf', 'w') as f:
                f.writelines(contents)
        try:
            run_as_root('/sbin/sysctl -p', ignore_error = True)
            current_value = int( get_output('/sbin/sysctl -n vm.swappiness').strip() )
            if current_value != new_value: raise CommandFailError
        except AccessDeniedError:
            pass
    
    apply_button = image_stock_button(gtk.STOCK_APPLY, _('Apply') )
    apply_button.connect('clicked', apply, adjustment)
    align_apply_button = gtk.HBox(False, 0)
    align_apply_button.pack_end(apply_button, False)
    
    vbox.pack_start(text_box, False, False)
    vbox.pack_start(scale, False, False)
    vbox.pack_start(align_apply_button, False, False)
    vbox.set_size_request(500, -1)
    align_vbox = gtk.Alignment(0, 0)
    align_vbox.add(vbox)
    return Setting(align_vbox, _('Change the tendency of swapping memory to disk'), ['memory'])

def __restart_network():
     def restart_network(w):
         try:
             import dbus
             bus = dbus.SystemBus()
             obj = bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
             obj.sleep(dbus_interface='org.freedesktop.NetworkManager')
             obj.wake(dbus_interface='org.freedesktop.NetworkManager')
             if Config.is_Ubuntu() or Config.is_Mint():
                 notify(' ', _('Run command: ')+'/etc/init.d/networking restart')
                 try:
                     run_as_root('/etc/init.d/networking restart')
                 except AccessDeniedError:
                     pass
             notify(_('Information'), _('Network restarted successfully.'))
         except: pass
     button_restart_network = gtk.Button(_('Restart network').center(30))
     button_restart_network.connect('clicked', restart_network)
     button_restart_network.set_tooltip_text(_('These commands will be executed:\n'
               'dbus-send --system --dest=org.freedesktop.NetworkManager '
               '--type=method_call /org/freedesktop/NetworkManager '
               'org.freedesktop.NetworkManager.sleep\n'
               'dbus-send --system --dest=org.freedesktop.NetworkManager '
               '--type=method_call /org/freedesktop/NetworkManager '
               'org.freedesktop.NetworkManager.wake\n'
               'sudo /etc/init.d/networking restart'))
     align_bfm = gtk.Alignment(0, 0.5)
     align_bfm.add(button_restart_network)
     vbox = gtk.VBox()
     vbox.set_border_width(10)
     vbox.pack_start(align_bfm, False)
     return Setting(vbox, _('Restart network'), ['network'])
 
def __change_hostname(): 
#   I have to use the class, to resolve problem of these codes:
#        def __value_changed(button):
#            button.set_sensitive(True)
#
#        def __button_clicked(entry):
#            new_host_name = entry.get_text()
#            button.set_sensitive(False)
#   error message is 'free variable referenced before assignment'. I don't know the reason.
    class change_host_name(gtk.HBox):
        def __value_changed(self, *w):
            self.button.set_sensitive(True)

        def __button_clicked(self, *w):
            new_host_name = self.entry.get_text()
            with TempOwn('/etc/hosts') as o:
                with open('/etc/hosts') as f:
                    content = f.read()
                    content = content.replace(self.old_host_name, new_host_name)
                with open('/etc/hosts', 'w') as f:
                    f.write(content)
            if Config.is_Ubuntu() or Config.is_Mint():
                with TempOwn('/etc/hostname') as o:
                    with open('/etc/hostname', 'w') as f:
                        f.write(new_host_name)
            elif Config.is_Fedora():
                with TempOwn('/etc/sysconfig/network') as o:
                    with open('/etc/sysconfig/network') as f:
                        content = f.read()
                        content = content.replace(self.old_host_name, new_host_name)
                    with open('/etc/sysconfig/network', 'w') as f:
                        f.write(content)       
            else:
                dialog = gtk.Dialog('Feature is not implemented', None, gtk.DIALOG_MODAL|gtk.DIALOG_NO_SEPARATOR,
                                     buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
                dialog.vbox.pack_start(gtk.Label('This feature has not been implement for your Linux distribution'))
                dialog.vbox.show_all()
                dialog.run()
                dialog.destroy()      
                            
            self.button.set_sensitive(False)
        
        def __init__(self):
            self.entry = gtk.Entry()
            self.button = gtk.Button(_('Apply'))
            self.label = gtk.Label(_('New host name:'))
            self.old_host_name = get_output('hostname')
            self.entry.set_text(self.old_host_name)
            self.entry.connect('changed', self.__value_changed)
            self.button.connect('clicked', self. __button_clicked)
                
            gtk.HBox.__init__(self, False, 5)
            self.pack_start(self.label, False)
            self.pack_start(self.entry, False)
            self.pack_start(self.button, False)
            
    hbox = change_host_name()
    return Setting(hbox, _('Change host name'), ['host_name'])

class Configure_Firefox(gtk.VBox):
    def __get_config_item(self):
        return [                
                ['user_pref("content.max.tokenizing.time", true);\n'
                 'user_pref("content.notify.ontimer", true);\n'
                 'user_pref("network.http.pipelining.firstrequest", true);\n'
                 'user_pref("network.http.pipelining.ssl", true);\n'
                 'user_pref("network.http.proxy.pipelining", true);\n'
                 'user_pref("content.max.tokenizing.time", 3000000);\n'
                 'user_pref("content.maxtextrun", 8191);\n'
                 'user_pref("content.notify.backoffcount", 200);\n'
                 'user_pref("content.notify.interval", 100000);\n'
                 'user_pref("content.notify.threshold", 100000);\n'
                 'user_pref("content.switch.threshold", 650000);\n'
                 'user_pref("network.dnsCacheEntries", 256);\n'
                 'user_pref("network.dnsCacheExpiration", 86400);\n'
                 'user_pref("network.ftp.idleConnectionTimeout", 60);\n'
                 'user_pref("network.http.keep-alive.timeout", 30);\n'
                 'user_pref("network.http.max-persistent-connections-per-proxy", 24);\n'
                 'user_pref("nglayout.initialpaint.delay", 0);\n'
                 'user_pref("network.http.pipelining.maxrequests", 8);\n'
                 'user_pref("network.http.max-connections", 96);\n'
                 'user_pref("network.http.max-connections-per-server", 32);\n'
                 'user_pref("network.http.max-persistent-connections-per-server", 8);\n'
                 'user_pref("ui.submenuDelay", 0);\n',
                 _('Speed up Firefox'),],
                 ['user_pref("browser.urlbar.autoFill", true);\n', _('Autofill in Urlbar'),],                 
                 ['user_pref("network.protocol-handler.app.ed2k", "/usr/bin/ed2k");\n'
                  'user_pref("network.protocol-handler.external.ed2k", true);\n', _('Support ed2k'),],                  
                 ['user_pref("config.trim_on_minimize", true);\n', _('Swap out memory when the program is minimized'),],
                 ['user_pref("network.prefetch-next", false);\n', _('Disable link prefetching'), ],                 
                 ['user_pref("security.dialog_enable_delay", 0);\n', _('Disable the delay of install extensions'), ],

                ]

    def __init__(self):
        gtk.VBox.__init__(self, False, 5)
        self.changed = 0
        self.button_apply = button_apply = image_stock_button(gtk.STOCK_APPLY, _('Apply') )
        button_apply.connect('clicked', self.__apply_change)
        button_apply.set_sensitive(True)
        align_button_apply = gtk.HBox(False, 0)
        align_button_apply.pack_end(button_apply, False)
        self.checkbuttons = []
        for msg in self.__get_config_item():
            self.checkbuttons.append( FirefoxConfig(self, *msg) )        
        btable = gtk.Table()
        btable.set_col_spacings(10)
        label = gtk.Label()
        label.set_text(_('Ailurus can help you setting the Firefox.  '
                         'Before tweak, you should make sure your Firefox closed.'))
        btable.attach(label, 0 , 2, 0, 1, gtk.FILL, gtk.FILL)
        X = 0
        Y = 1
        for button in self.checkbuttons:
            btable.attach(button, X, X+1, Y, Y+1, gtk.FILL, gtk.FILL)
            X+=1
            if X==2: ( X,Y ) = ( 0,Y+1 )
        btable.attach(align_button_apply, 1, 2, Y+1, Y+2, gtk.FILL, gtk.FILL)
        self.pack_start(btable, False)

    def __apply_change(self, w):
        install_package = []
        for button in self.checkbuttons:
            if button.get_active():
                install_package.append(button.config_item)
        import os
        path = os.path.expanduser('~/.mozilla/firefox/' + FirefoxExtensions.get_extensions_path().split('/')[5] + '/')
        if not os.path.isfile(path + 'user.js.bak'):
            run('cp ' + path + 'prefs.js ' + path + 'prefs.js.bak')
        run('cp ' + path + 'prefs.js.bak ' + path + 'prefs.js')
        f = open(path + 'user.js', 'w+')
        f.writelines(install_package)
        f.close()
        notify(_('Setting Success!'), _('Please restart Firefox to make setting effect!'))
        
def __firefox_config_panel():
    if FirefoxExtensions.get_extensions_path()!='':
        return Setting(Configure_Firefox(), _('Firefox Advance Setting'),
                   ['firefox'])
    else:
        hbox = gtk.HBox()
        label = gtk.Label()
        label.set_text(_('Ailurus cannot find Firefox Setting File. \n'
                         'Please make sure Firefox have installed in your computer.\n'))
        hbox.pack_start(label, False, False)
        return Setting(hbox, _('Firefox Advance Setting'), ['firefox'])
    
def get():
    ret = []
    for f in [
            __change_kernel_swappiness,
            __change_hostname,
            __firefox_config_panel,
            __restart_network ]:
        try:
            ret.append(f())
        except:
            import traceback
            traceback.print_exc()
    return ret
