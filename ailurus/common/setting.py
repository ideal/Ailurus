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
        run_as_root('/sbin/sysctl -p', ignore_error = True)
        current_value = int( get_output('/sbin/sysctl -n vm.swappiness').strip() )
        if current_value != new_value: raise CommandFailError
    
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
             if UBUNTU or UBUNTU_DERIV:
                 notify(' ', _('Run command: ')+'/etc/init.d/networking restart')
                 run_as_root('/etc/init.d/networking restart')
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
            if UBUNTU or UBUNTU_DERIV:
                with TempOwn('/etc/hostname') as o:
                    with open('/etc/hostname', 'w') as f:
                        f.write(new_host_name)
            elif FEDORA:
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

def __configure_firefox():
    if not firefox.support: return None
    
    global table, row
    table = gtk.Table()
    table.set_row_spacings(5)
    row = 0

    explain = gtk.Label(_('Tweak Firefox by changing file %s.\n'
                          'Please close all Firefox windows.') % firefox.prefs_js_path)
    explain.set_alignment(0, 0.5)
    explain.set_selectable(True)
    table.attach(explain, 0, 2, row, row+1, gtk.FILL, gtk.FILL)
    row += 1

    tweak_key = gtk.Button()
    tweak_key = image_stock_button(gtk.STOCK_APPLY, _('Auto tweak Firefox') )
    table.attach(left_align(tweak_key), 0, 2, row, row+1, gtk.FILL, gtk.FILL)
    row += 1

    # DNS
    dns_entries = FirefoxNumericPref('network.dnsCacheEntries', default=20)
    dns_entries_t = FirefoxPrefText(_('the number of DNS results to cache'), 'network.dnsCacheEntries')
    dns_expiration = FirefoxNumericPref('network.dnsCacheExpiration', default=60)
    dns_expiration_t = FirefoxPrefText(_('the number of seconds to cache DNS results'), 'network.dnsCacheExpiration')
    # connection number and timeout
    ftp_timeout = FirefoxNumericPref('network.ftp.idleConnectionTime', default=300)
    ftp_timeout_t = FirefoxPrefText(_('the number of seconds before the FTP connection times out'), 'network.ftp.idleConnectionTimeout')
    alive_connection_timeout = FirefoxNumericPref('network.http.keep-alive.timeout', default=300)
    alive_connection_timeout_t = FirefoxPrefText(_('amount of time in seconds to keep alive connections'), 'network.http.keep-alive.timeout', 
                                                 _('alive connections can be re-used for multiple requests to improve performance'))
    max_connections = FirefoxNumericPref('network.http.max-connections', default=30)
    max_connections_t = FirefoxPrefText(_('the maximum number of HTTP connections'), 'network.http.max-connections',
                                        _('Users on slower connections may want to reduce this number to prevent HTTP connection timeouts.\n'
                                          'Users on faster connections may want to increase it.'))
    max_connections_per_server = FirefoxNumericPref('network.http.max-connections-per-server', default=15)
    max_connections_per_server_t = FirefoxPrefText(_('the maximum number of connections to a single server'), 'network.http.max-connections-per-server')
    max_connections_per_proxy = FirefoxNumericPref('network.http.max-persistent-connections-per-proxy', default=8)
    max_connections_per_proxy_t = FirefoxPrefText(_('the total number of alive connections per proxy server'),
                                                    'network.http.max-persistent-connections-per-proxy')
    # Page rendering
    initialpaint_delay = FirefoxNumericPref('nglayout.initialpaint.delay', default=250)
    initialpaint_delay_t = FirefoxPrefText(_('the number of milliseconds to wait before first displaying the page'), 'nglayout.initialpaint.delay',
                                           _("Since the start of a web page normally doesn't have much useful information to display,\n"
                                             "Firefox will wait a short interval before first rendering a page."))
    max_time_between_reflow = FirefoxNumericPref('content.max.tokenizing.time', default=360000)
    max_time_between_reflow_t = FirefoxPrefText(_('the maximum number of microseconds between two page rendering'), 'content.max.tokenizing.time')
    max_reflow_time = FirefoxNumericPref('content.notify.backoffcount', default=-1)
    max_reflow_time_t = FirefoxPrefText(_('re-render pages until this number has been reached (-1 means unlimited)'), 'content.notify.backoffcount')
    # page content
    gif_mode = FirefoxComboPref('image.animation_mode', [_('loop'), _('only once'), _('never'),], ['normal', 'once', 'none'], default='normal')
    gif_mode_t = FirefoxPrefText(_('how to animate GIF images'), 'image.animation_mode')
    show_blink = FirefoxBooleanPref('browser.blink_allowed', default=True)
    show_blink_t = FirefoxPrefText(_('display content in &lt;blink&gt; elements and styled with text-decoration:blink as blinking text'), 'browser.blink_allowed')
    # tab
    max_undo_tabs = FirefoxNumericPref('browser.sessionstore.max_tabs_undo', default=10)
    max_undo_tabs_t = FirefoxPrefText(_('how many closed tabs are kept track'), 'browser.sessionstore.max_tabs_undo')
    min_tab_width = FirefoxNumericPref('browser.tabs.tabMinWidth', default=100)
    min_tab_width_t = FirefoxPrefText(_('the width of narrowest tab'), 'browser.tabs.tabMinWidth',
                                      _("To fit more tabs on the tab strip, Firefox shrinks every tab.\n"
                                        "This preference determines the narrowest a tab can become before the tab strip becomes scrollable."))
    tab_scroll_step = FirefoxNumericPref('toolkit.scrollbox.scrollIncrement', default=20)
    tab_scroll_step_t = FirefoxPrefText(_("how many pixels to scroll at a time when scrolling the tab strip's scrollbox"), 
                                        'toolkit.scrollbox.scrollIncrement',
                                        _('When there is a large number of tabs, you can scroll the tab strip horizontally to see all available tabs.\n'
                                          'This preference specifies how quickly the strip scrolls.'))
    # urlbar
    urlbar_autofill = FirefoxBooleanPref('browser.urlbar.autoFill', default=False)
    urlbar_autofill_t = FirefoxPrefText(_('auto complete url-bar, display entries you have previously typed that closely match the text your typed'),
                                        'browser.urlbar.autoFill')
    # history
    history_expire_days = FirefoxNumericPref('browser.history_expire_days', default=180)
    history_expire_days_t = FirefoxPrefText(_('how many days in which history entries are expired'), 'browser.history_expire_days')
    history_expire_sites = FirefoxNumericPref('browser.history_expire_sites', default=40000)
    history_expire_sites_t = FirefoxPrefText(_('the maximum number of websites to keep in history'), 'browser.history_expire_sites')
    # misc
    cache_capacity = FirefoxNumericPref('browser.cache.offline.capacity', default=512000)
    cache_capacity_t = FirefoxPrefText(_('the amount of disk space the offline cache may use (in kilobytes)'), 'browser.cache.offline.capacity')
    addons_max_results = FirefoxNumericPref('extension.getAddons.maxResults', default=5)
    addons_max_results_t = FirefoxPrefText(_('the maximum number of results to display in the "Get Add-ons" dialog'), 'extension.getAddons.maxResults')
    backspace_action = FirefoxComboPref('browser.backspace_action',
                                        [_('go back'), _('scroll up'), _('do nothing')],
                                        [0, 1, 2],
                                        default=2)
    backspace_action_t = FirefoxPrefText(_('when press the Backspace button'), 'browser.backspace_action' )

    def add(t, w):
        global table, row
        table.attach(t, 0, 1, row, row+1, gtk.FILL|gtk.EXPAND, gtk.FILL)
        table.attach(w, 1, 2, row, row+1, 0, gtk.FILL)
        row += 1

    def add2(text):
        global table, row
        assert isinstance(text, (str, unicode)) and text
        label = gtk.Label()
        label.set_markup('<b>%s</b>' % text)
        label.set_alignment(0, 0.5)
        table.attach(label, 0, 1, row, row+1, gtk.FILL|gtk.EXPAND, gtk.FILL)
        row += 1
    
    add2(_('DNS'))
    add(dns_entries_t, dns_entries)
    add(dns_expiration_t, dns_expiration)
    add2(_('connections number and timeout'))
    add(ftp_timeout_t, ftp_timeout)
    add(alive_connection_timeout_t, alive_connection_timeout)
    add(max_connections_t, max_connections)
    add(max_connections_per_server_t, max_connections_per_server)
    add(max_connections_per_proxy_t, max_connections_per_proxy)
    add2(_('page rendering'))
    add(initialpaint_delay_t, initialpaint_delay)
    add(max_time_between_reflow_t, max_time_between_reflow)
    add(max_reflow_time_t, max_reflow_time)
    add2(_('page content'))
    add(gif_mode_t, gif_mode)
    add(show_blink_t, show_blink)
    add2(_('tab'))
    add(max_undo_tabs_t, max_undo_tabs)
    add(min_tab_width_t, min_tab_width)
    add(tab_scroll_step_t, tab_scroll_step)
    add2(_('miscellaneous'))
    add(cache_capacity_t, cache_capacity)
    add(history_expire_days_t, history_expire_days)
    add(history_expire_sites_t, history_expire_sites)
    add(urlbar_autofill_t, urlbar_autofill)
    add(addons_max_results_t, addons_max_results)
    add(backspace_action_t, backspace_action)
    
    def tweak():
        dns_entries.set_value(256)
        dns_expiration.set_value(86400)
        ftp_timeout.set_value(60)
        alive_connection_timeout.set_value(30)
        max_connections.set_value(100)
        max_connections_per_server.set_value(32)
        max_connections_per_proxy.set_value(24)
        initialpaint_delay.set_value(0)
        max_time_between_reflow.set_value(3000000)
        max_reflow_time.set_value(200)
    tweak_key.connect('clicked', lambda w: tweak())
   
    return Setting(table, _('Configure Firefox'), ['firefox'])
    
def get():
    ret = []
    for f in [
            __change_kernel_swappiness,
            __change_hostname,
            __configure_firefox,
            __restart_network ]:
        try:
            a = f()
            if a: ret.append(a) # if such function is not supported, f() returns None.
        except:
            print_traceback()
    return ret
