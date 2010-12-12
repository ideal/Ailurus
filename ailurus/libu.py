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

def title_label(text):
    import gtk
    label = gtk.Label()
    label.set_markup('<b>%s</b>'%text)
    label.set_alignment(0, 0)
    return label

def copy_to_clipboard(text):
    assert isinstance(text, str)
    import gtk
    clipboard = gtk.clipboard_get()
    clipboard.set_text(text)

def get_clipboard_text():
    import gtk
    clipboard = gtk.clipboard_get()
    return clipboard.wait_for_text()

def scale_image(old_path, new_path, new_width, new_height):
    import gtk
    pixbuf = gtk.gdk.pixbuf_new_from_file(old_path)
    pixbuf = pixbuf.scale_simple(new_width, new_height, gtk.gdk.INTERP_HYPER)
    pixbuf.save(new_path, 'png')
        
def blank_pixbuf(width, height):
    import gtk
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
    pixbuf.fill(0) # transparent black
    return pixbuf

def get_pixbuf(path, width, height):
    import os, gtk
    if os.path.exists(path): return gtk.gdk.pixbuf_new_from_file_at_size(path, width, height)
    else:
        print path, 'is missing'
        return blank_pixbuf(width, height)

def gray_bg(widget):
    import gtk
    if not isinstance(widget, gtk.Entry) and not isinstance(widget, gtk.TextView): raise TypeError
    
    def event(widget, e):
        if widget.base_color_changed==False:
            color = widget.style.bg[gtk.STATE_NORMAL]
            widget.modify_base(gtk.STATE_NORMAL, color)
            widget.base_color_changed = True
    widget.base_color_changed = False
    widget.connect('expose-event', event)
    widget.connect('map-event', event)

def long_text_label(text):
    import gtk
    textview = gtk.TextView()
    gray_bg(textview)
    textview.set_wrap_mode(gtk.WRAP_WORD)
    textview.set_cursor_visible(False)
    textview.set_editable(False)
    textview.get_buffer().set_text(text)
    return textview
    
def image_stock_button(stock, text):
    import gtk
    box = gtk.HBox(False, 3)
    box.pack_start(gtk.image_new_from_stock(stock, gtk.ICON_SIZE_BUTTON), False, False)
    l = gtk.Label()
    l.set_text_with_mnemonic(text)
    box.pack_start(l, False, False)
    button = gtk.Button()
    button.add(box)
    return button

def image_file_button(label, image_file_name, size):
    import gtk
    pixbuf = get_pixbuf(image_file_name, size, size)
    image = gtk.Image()
    image.set_from_pixbuf(pixbuf)
    box = gtk.HBox(False, 3)
    box.pack_start(image, False, False)
    l = gtk.Label()
    l.set_text_with_mnemonic(label)
    box.pack_start(l, False, False)
    button = gtk.Button()
    button.add(box)
    return button

def stock_image_only_button(stock):
    import gtk
    image = gtk.image_new_from_stock(stock, gtk.ICON_SIZE_BUTTON)
    button = gtk.Button()
    button.add(image)
    return button

def image_file_only_button(image_file_path, size):
    import gtk
    pixbuf = get_pixbuf(image_file_path, size, size)
    image = gtk.image_new_from_pixbuf(pixbuf)
    button = gtk.Button()
    button.add(image)
    return button

def image_stock_menuitem(image_stock, label):
    import gtk
    item = gtk.ImageMenuItem(stock_id=image_stock)
    item.get_child().set_text(label)
    return item

def image_file_menuitem(label, image_file_name, size):
    import gtk
    pixbuf = get_pixbuf(image_file_name, size, size)
    image = gtk.Image()
    image.set_from_pixbuf(pixbuf)
    item = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
    item.set_image(image)
    item.get_child().set_text(label)
    return item
    
def title_menuitem(string):
    import gtk
    l = gtk.Label()
    l.set_markup('<span size="large"><b>%s</b></span>'%string)
    box = gtk.HBox(False, 3)
    box.pack_start(l, False, False)
    item = gtk.MenuItem()
    item.add(box)
#    item.select()
    def dummy(*w):
        return True
    item.connect('enter-notify-event', dummy)
    item.connect('leave-notify-event', dummy)
    item.connect('button-press-event', dummy)
    item.connect('button-release-event', dummy)
    return item

def left_align(widget):
    import gtk
    align = gtk.Alignment(0, 0.5)
    align.add(widget)
    return align

def center_align(widget):
    import gtk
    align = gtk.Alignment(0.5, 0.5)
    align.add(widget)
    return align

def right_align(widget):
    import gtk
    align = gtk.Alignment(1, 0.5)
    align.add(widget)
    return align
    
def label_left_align(string):
    import gtk
    label = gtk.Label(string)
    return left_align(label)

def image_left_align(path):
    import gtk
    image = gtk.Image()
    image.set_from_file(path)
    return image

def add_expander(vbox, title):
    def __title(text):
        label = gtk.Label()
        label.set_markup('<b>%s</b>'%text)
        return label

    import gtk
    expander = gtk.Expander()
    expander.set_border_width(5)
    expander.set_label_widget( __title(title) )
    vbox.set_border_width(5)
    expander.add(vbox)
    expander.set_expanded(False)
    return expander

def show_text_window(title, content, show_textbox_border = True, show_a_big_window = True):
    import gtk
    buffer = gtk.TextBuffer()
    buffer.set_text(content)
    textview = gtk.TextView()
    textview.set_buffer(buffer)
    textview.set_editable(False)
    textview.set_cursor_visible(False)
    textview.set_wrap_mode(gtk.WRAP_WORD)
    gray_bg(textview)
    scroll = gtk.ScrolledWindow()
    scroll.add(textview)
    scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    if show_textbox_border:
        scroll.set_shadow_type(gtk.SHADOW_IN)
    copy = image_stock_button(gtk.STOCK_COPY, _('Copy text to clipboard'))
    def clicked():
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        copy_to_clipboard(buffer.get_text(start, end))
    copy.connect('clicked', lambda w: clicked())
    close_button = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
    close_button.connect('clicked', lambda *w: window.destroy())
    buttonbox = gtk.HBox(False, 10)
    buttonbox.pack_end(close_button, False)
    buttonbox.pack_end(copy, False)
    vbox = gtk.VBox(False, 10)
    vbox.pack_start(scroll)
    vbox.pack_start(buttonbox, False)

    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title(title)
    window.add(vbox)
    if show_a_big_window:
        window.set_default_size(600, 400)
    window.set_border_width(10)
    window.set_position(gtk.WIN_POS_CENTER)
    window.show_all()

def do_access_denied_error():
    import gtk
    message = _('Operation is canceled because you refused authentication.\n'
                'Authentication is provided by system PolicyKit service.\n'
                'Ailurus does not know your password at all.')
    label = gtk.Label(message)
    label.set_alignment(0, 0.5)
    button_close = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
    button_close.connect('clicked', lambda w: window.destroy())
    vbox = gtk.VBox(False, 5)
    vbox.pack_start(label, False)
    vbox.pack_start(right_align(button_close), False)
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title(_('Operation is canceled'))
    window.set_border_width(10)
    window.set_position(gtk.WIN_POS_CENTER)
    window.add(vbox)
    window.show_all()

def do_gnomekeyring_cancelled_error():
    import gtk
    message = _('Operation is canceled because you refused authentication.\n'
                'Proxy string is saved in system GNOME keyring service.\n'
                'Ailurus does not know your secret at all.')
    label = gtk.Label(message)
    label.set_alignment(0, 0.5)
    button_close = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
    button_close.connect('clicked', lambda w: window.destroy())
    vbox = gtk.VBox(False, 5)
    vbox.pack_start(label, False)
    vbox.pack_start(right_align(button_close), False)
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title(_('Operation is canceled'))
    window.set_border_width(10)
    window.set_position(gtk.WIN_POS_CENTER)
    window.add(vbox)
    window.show_all()

def do_apt_source_syntax_error(value):
    import gtk, StringIO
    msg = StringIO.StringIO()
    print >>msg,  _('Source configuration has syntax error. Please run the following command to fix error.')
    print >>msg, '<span color="blue">%s</span>' % 'sudo gedit /etc/apt/sources.list /etc/apt/sources.list.d/*.list'
    print >>msg
    print >>msg, _('Error reason:')
    print >>msg, '<span color="blue">%s</span>' % value
    print >>msg
    print >>msg, _('After fixing the error, Ailurus will work fine.')
    
    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE)
    dialog.set_title(_('Fatal error'))
    dialog.set_position(gtk.WIN_POS_CENTER)
    dialog.set_markup(msg.getvalue())
    dialog.show_all()
    dialog.run()
    dialog.destroy()
    
    import sys
    sys.exit()

def exception_happened(etype, value, tb):
    import traceback, StringIO, os, sys, platform, gtk, gnomekeyring
    from lib import AILURUS_VERSION, D, AccessDeniedError, APTSourceSyntaxError, report_bug

    if etype == KeyboardInterrupt: return
    if etype == AccessDeniedError: return do_access_denied_error()
    if etype == APTSourceSyntaxError: return do_apt_source_syntax_error(value)
    if etype == gnomekeyring.CancelledError: return do_gnomekeyring_cancelled_error()
    
    traceback.print_tb(tb, file=sys.stderr)
    sys.stderr.flush()
    msg = StringIO.StringIO()
    traceback.print_tb(tb, file=msg)
    print >>msg, etype, ':', value
    print >>msg, platform.dist()
    print >>msg, os.uname()
    print >>msg, 'Ailurus version:', AILURUS_VERSION

    title_box = gtk.HBox(False, 5)
    if os.path.exists(D+'umut_icons/bug.png'):
        image = gtk.Image()
        image.set_from_file(D+'umut_icons/bug.png')
        title_box.pack_start(image, False)
    title = label_left_align(_('A bug appears. Would you please tell Ailurus developers? Thank you!') + 
                             '\n' + _('Please copy and paste following text into bug report web-page.'))
    title_box.pack_start(title, False)
    
    textview_traceback = gtk.TextView()
    gray_bg(textview_traceback)
    textview_traceback.set_wrap_mode(gtk.WRAP_WORD)
    textview_traceback.get_buffer().set_text(msg.getvalue())
    textview_traceback.set_cursor_visible(False)
    scroll_traceback = gtk.ScrolledWindow()
    scroll_traceback.set_shadow_type(gtk.SHADOW_IN)
    scroll_traceback.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroll_traceback.add(textview_traceback)
    scroll_traceback.set_size_request(-1, 300)
    button_copy = image_stock_button(gtk.STOCK_COPY, _('Copy text to clipboard'))
    def clicked():
        buffer = textview_traceback.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        copy_to_clipboard(buffer.get_text(start, end))
    button_copy.connect('clicked', lambda w: clicked())
    button_report_bug = image_stock_button(gtk.STOCK_DIALOG_WARNING, _('Click here to report bug via web-page') )
    button_report_bug.connect('clicked', lambda w: report_bug() )
    button_close = image_stock_button(gtk.STOCK_CLOSE, _('Close'))
    button_close.connect('clicked', lambda w: window.destroy())
    bottom_box = gtk.HBox(False, 10)
    bottom_box.pack_end(button_close, False)
    bottom_box.pack_end(button_report_bug, False)
    bottom_box.pack_end(button_copy, False)
    
    vbox = gtk.VBox(False, 5)
    vbox.pack_start(title_box, False)
    vbox.pack_start(scroll_traceback)
    vbox.pack_start(bottom_box, False)
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title(_('Bug appears!'))
    window.set_border_width(10)
    window.add(vbox)
    window.show_all()
