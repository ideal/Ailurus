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
from lib import *
from libu import *
import urllib
import gtk, pango

class ProposeLinuxSkillWindow(gtk.Window):
    def save(self, linuxskill):
        with open(Config.config_dir + 'proposed_linuxskill', 'a') as f:
            f.write(linuxskill.strip())
            f.write('\n'
                    '#################'
                    '\n')
    
    def read(self):
        try:
            with open(Config.config_dir + 'proposed_linuxskill') as f:
                return f.read()
        except:
            return ''
    
    def show_contact(self):
        contact = Config.get_contact()
        self.contact_entry.set_text(contact)

    def set_contact(self, value):
        Config.set_contact(value)
        self.contact_entry.set_text(value)

    def do_submit(self):
        contact = self.contact_entry.get_text()
        buffer = self.content.get_buffer()
        linux_skill = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        if not linux_skill: return
        try:
            add_linuxskill(linux_skill, contact)
        except:
            print_traceback()
            message = _('Cannot upload Linux skill.\n'
                        'Would you please email Linux skill to Ailurus developers? Thank you!')
            dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK,
                                       message_format = message)
            dict = {'subject': 'Linux_skill', 'body': linux_skill}
            url = 'mailto:homer.xing@gmail.com?' + urllib.urlencode(dict)
            email_button = url_button(url, _('Click here'))
            align = gtk.Alignment(0.5, 0.5)
            align.add(email_button)
            dialog.vbox.pack_start(align, False)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
        else:
            dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK,
                                       message_format = _('Successfully uploaded Linux skill.\n'
                                                          'Thank you very much!'))
            dialog.run()
            dialog.destroy()
            self.save(linux_skill)
            self.destroy()

        if not contact: contact = _('Anonymous')
        Config.set_contact(contact)

    def __init__(self):
        label1 = gtk.Label(_('Thank you very much!'))
        label1.set_alignment(0, 0.5)
        
        self.contact_entry = contact_entry = gtk.Entry()
        contact_entry.modify_font(pango.FontDescription('Georgia'))
        anonymous = gtk.Button(_('Anonymous'))
        anonymous.connect('clicked', lambda *w: self.set_contact(_('Anonymous')))
        contact_box = gtk.HBox(False, 5)
        contact_box.pack_start(gtk.Label(_('Name or Email:')), False)
        contact_box.pack_start(contact_entry)
        contact_box.pack_start(anonymous, False)
        
        label2 = gtk.Label(_('Linux skill:'))
        label2.set_alignment(0, 0.5)
        
        self.content = content = gtk.TextView()
        content.set_wrap_mode(gtk.WRAP_WORD)
        content.modify_font(pango.FontDescription('Georgia'))
        content_scroll = gtk.ScrolledWindow()
        content_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        content_scroll.set_shadow_type(gtk.SHADOW_IN)
        content_scroll.add(content)

        submit_button = gtk.Button(stock=gtk.STOCK_OK)
        submit_button.connect('clicked', lambda *w: self.do_submit())
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel_button.connect('clicked', lambda *w: self.destroy())
        button_box = gtk.HBox(False, 5)
        button_box.pack_end(cancel_button, False)
        button_box.pack_end(submit_button, False)

        proposed = self.read()
        if not proposed:
            proposed = _('(Empty)')
        textview_proposed = gtk.TextView()
        textview_proposed.set_wrap_mode(gtk.WRAP_WORD)
        textview_proposed.modify_font(pango.FontDescription('Georgia'))
        textview_proposed.get_buffer().set_text(proposed)
        scroll_proposed = gtk.ScrolledWindow()
        scroll_proposed.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll_proposed.set_shadow_type(gtk.SHADOW_IN)
        scroll_proposed.add(textview_proposed)
        expander = gtk.Expander(_('Your proposed Linux skills'))
        expander.set_expanded(False)
        expander.add(scroll_proposed)

        vbox = gtk.VBox(False, 5)
        vbox.pack_start(label1, False)
        vbox.pack_start(contact_box, False)
        vbox.pack_start(label2, False)
        vbox.pack_start(content_scroll)
        vbox.pack_start(button_box, False)
        vbox.pack_start(expander, False)
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title(_('Propose a Linux skill'))
        self.set_border_width(5)
        self.add(vbox)
        self.set_focus(content)
        self.set_default_size(-1, 400)
        self.show_all()
        
        self.show_contact()

class ProposeSuggestionWindow(gtk.Window):
    def save(self, linuxskill):
        with open(Config.config_dir + 'proposed_suggestion', 'a') as f:
            f.write(linuxskill.strip())
            f.write('\n'
                    '#################'
                    '\n')
    
    def read(self):
        try:
            with open(Config.config_dir + 'proposed_suggestion') as f:
                return f.read()
        except:
            return ''
    
    def show_contact(self):
        contact = Config.get_contact()
        self.contact_entry.set_text(contact)

    def set_contact(self, value):
        Config.set_contact(value)
        self.contact_entry.set_text(value)

    def do_submit(self):
        contact = self.contact_entry.get_text()
        buffer = self.content.get_buffer()
        suggestion = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        if not suggestion: return
        try:
            add_suggestion(suggestion, contact)
        except:
            print_traceback()
            message = _('Cannot upload suggestion.\n'
                        'Would you please email suggestion to Ailurus developers? Thank you!')
            dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK,
                                       message_format = message)
            dict = {'subject': 'Suggestion', 'body': suggestion}
            url = 'mailto:homer.xing@gmail.com?' + urllib.urlencode(dict)
            email_button = url_button(url, _('Click here'))
            align = gtk.Alignment(0.5, 0.5)
            align.add(email_button)
            dialog.vbox.pack_start(align, False)
            dialog.show_all()
            dialog.run()
            dialog.destroy()
        else:
            dialog = gtk.MessageDialog(buttons = gtk.BUTTONS_OK,
                                       message_format = _('Successfully uploaded suggestion.\n'
                                                          'Thank you very much!'))
            dialog.run()
            dialog.destroy()
            self.save(suggestion)
            self.destroy()

        if not contact: contact = _('Anonymous')
        Config.set_contact(contact)

    def __init__(self):
        label1 = gtk.Label(_('Thank you very much!'))
        label1.set_alignment(0, 0.5)
        
        self.contact_entry = contact_entry = gtk.Entry()
        contact_entry.modify_font(pango.FontDescription('Georgia'))
        anonymous = gtk.Button(_('Anonymous'))
        anonymous.connect('clicked', lambda *w: self.set_contact(_('Anonymous')))
        contact_box = gtk.HBox(False, 5)
        contact_box.pack_start(gtk.Label(_('Name or Email:')), False)
        contact_box.pack_start(contact_entry)
        contact_box.pack_start(anonymous, False)
        
        label2 = gtk.Label(_('Suggestion:'))
        label2.set_alignment(0, 0.5)
        
        self.content = content = gtk.TextView()
        content.set_wrap_mode(gtk.WRAP_WORD)
        content.modify_font(pango.FontDescription('Georgia'))
        content_scroll = gtk.ScrolledWindow()
        content_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        content_scroll.set_shadow_type(gtk.SHADOW_IN)
        content_scroll.add(content)

        submit_button = gtk.Button(stock=gtk.STOCK_OK)
        submit_button.connect('clicked', lambda *w: self.do_submit())
        cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel_button.connect('clicked', lambda *w: self.destroy())
        button_box = gtk.HBox(False, 5)
        button_box.pack_end(cancel_button, False)
        button_box.pack_end(submit_button, False)

        proposed = self.read()
        if not proposed:
            proposed = _('(Empty)')
        textview_proposed = gtk.TextView()
        textview_proposed.set_wrap_mode(gtk.WRAP_WORD)
        textview_proposed.modify_font(pango.FontDescription('Georgia'))
        textview_proposed.get_buffer().set_text(proposed)
        scroll_proposed = gtk.ScrolledWindow()
        scroll_proposed.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll_proposed.set_shadow_type(gtk.SHADOW_IN)
        scroll_proposed.add(textview_proposed)
        expander = gtk.Expander(_('Your proposed Suggestions'))
        expander.set_expanded(False)
        expander.add(scroll_proposed)

        vbox = gtk.VBox(False, 5)
        vbox.pack_start(label1, False)
        vbox.pack_start(contact_box, False)
        vbox.pack_start(label2, False)
        vbox.pack_start(content_scroll)
        vbox.pack_start(button_box, False)
        vbox.pack_start(expander, False)
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title(_('Propose suggestion'))
        self.set_border_width(5)
        self.add(vbox)
        self.set_focus(content)
        self.set_default_size(-1, 400)
        self.show_all()
        
        self.show_contact()

if __name__ == '__main__': # test
    window = ProposeSuggestionWindow()
    gtk.main()