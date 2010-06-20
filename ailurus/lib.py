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

def get_icons_path():
    import os
    return os.path.dirname(os.path.abspath(__file__))+'/icons/'

def row(text, value, icon, tooltip = None): # only used in hardwareinfo.py and osinfo.py
    return (text, value, icon, tooltip)

class I:
    this_is_an_installer = True
    this_is_a_repository = False
    sane = True # False means installed() == False after calling install()
    category = 'others'
    detail = ''
    how_to_install = ''
    download_url = ''
    def self_check(self):
        'check errors in source code'
    def fill(self):
        'fill self.detail, self.how_to_install'
    def install(self):
        raise NotImplementedError
    def installed(self):
        raise NotImplementedError
    def remove(self):
        raise NotImplementedError
    def add_temp_repository(self):
        'Add repository before installing me'
    def clean_temp_repository(self):
        'Remove repository after installing me'

class C:
    this_is_a_cure = True
    MUST_FIX, SUGGESTION = range(2)
    type = SUGGESTION
    detail = ''
    def exists(self):
        raise NotImplementedError
    def cure(self):
        raise NotImplementedError
    
class Config:
    import os
    config_dir = os.path.expanduser('~/.config/ailurus/')
    @classmethod
    def make_config_dir(cls):
        import os
        dir = os.path.expanduser('~/.config/ailurus/')
        if not os.path.exists(dir): # make directory
            try:    os.makedirs(dir)
            except: pass # directory exists
        if os.stat(dir).st_uid != os.getuid(): # change owner
            run_as_root('chown $USER:$USER "%s"'%dir)
        if not os.access(dir, os.R_OK|os.W_OK|os.X_OK): # change access mode
            os.chmod(dir, 0755)
    @classmethod
    def get_config_dir(cls):
        return cls.config_dir
    @classmethod
    def init(cls):
        assert not hasattr(cls, 'inited')
        cls.inited = True
        # create parser object
        import ConfigParser, os
        cls.parser = ConfigParser.RawConfigParser()
        # read configuration file if it exists
        cls.make_config_dir()
        path = cls.get_config_dir() + 'conf'
        if os.path.exists(path):
            cls.parser.read(path)
    @classmethod
    def save(cls):
        cls.make_config_dir()
        with open(cls.get_config_dir() + 'conf' , 'w') as f:
            cls.parser.write(f)
    @classmethod
    def set_string(cls, key, value):
        assert isinstance(key, str) and key
        assert isinstance(value, (str,unicode))  and value
        cls.parser.set('DEFAULT', key, value)
        cls.save()
    @classmethod
    def get_string(cls, key):
        assert isinstance(key, str) and key
        return cls.parser.get('DEFAULT', key)
    @classmethod
    def set_int(cls, key, value):
        assert isinstance(key, str) and key
        assert isinstance(value, int), type(value)
        cls.parser.set('DEFAULT', key, value)
        cls.save()
    @classmethod
    def get_int(cls, key):
        assert isinstance(key, str) and key
        value = cls.parser.get('DEFAULT', key)
        return int(value)
    @classmethod
    def set_long(cls, key, value):
        assert isinstance(key, str) and key
        assert isinstance(value, long), type(value)
        cls.parser.set('DEFAULT', key, value)
        cls.save()
    @classmethod
    def get_long(cls, key):
        assert isinstance(key, str) and key
        value = cls.parser.get('DEFAULT', key)
        return long(value)
    @classmethod
    def set_bool(cls, key, value):
        assert isinstance(key, str) and key
        assert isinstance(value, bool)
        cls.parser.set('DEFAULT', key, value)
        cls.save()
    @classmethod
    def get_bool(cls, key):
        assert isinstance(key, str) and key
        value = cls.parser.get('DEFAULT', key)
        value = str(value)
        return value=='True' or value=='true'
    @classmethod
    def set_login_window_background(cls, value):
        'just a cache. value may be wrong. cache the gconf value "/desktop/gnome/background/picture_filename" of user "gdm".'
        cls.set_string('login_window_background', value)
    @classmethod
    def get_login_window_background(cls):
        return cls.get_string('login_window_background') # please do not catch exception
    @classmethod
    def set_last_check_update_time_to_now(cls):
        import time
        value = long(time.time()) # the time as a floating point number expressed in seconds since the epoch, in UTC
        cls.set_long('last_check_update_time', value)
    @classmethod
    def get_last_check_update_time(cls):
        try: return cls.get_long('last_check_update_time')
        except: return 0
    @classmethod
    def is_long_enough_since_last_check_update(cls):
        import time
        last_check_time = cls.get_last_check_update_time()
        now = time.time() # the time as a floating point number expressed in seconds since the epoch, in UTC
        one_day = 3600 * 24
        return now - last_check_time > one_day * 14
    @classmethod
    def set_synced(cls): # has synchronized latest application data?
        cls.set_bool('synced', True)
    @classmethod
    def get_synced(cls):
        try: return cls.get_bool('synced')
        except: return False
    @classmethod
    def set_use_proxy(cls, value):
        cls.set_bool('use_proxy', value)
    @classmethod
    def get_use_proxy(cls):
        try: return cls.get_bool('use_proxy')
        except: return False
    @classmethod
    def set_proxy_string_id_in_keyring(cls, value):
        cls.set_long('proxy_string_id_in_keyring', value)
    @classmethod
    def get_proxy_string_id_in_keyring(cls):
        # do not wrap it in try..except
        return cls.get_long('proxy_string_id_in_keyring')
    @classmethod
    def set_show_quick_setup_area(cls, value):
        cls.set_bool('show_quick_setup_area', value)
    @classmethod
    def get_show_quick_setup_area(cls):
        try:        return cls.get_bool('show_quick_setup_area')
        except:     return True
    @classmethod
    def set_show_sync_area(cls, value):
        cls.set_bool('show_sync_area', value)
    @classmethod
    def get_show_sync_area(cls):
        try:        return cls.get_bool('show_sync_area')
        except:     return True
    @classmethod
    def set_query_before_exit(cls, value):
        cls.set_bool('query_before_exit', value)
    @classmethod
    def get_query_before_exit(cls):
        try:       return cls.get_bool('query_before_exit')
        except:    return True
    @classmethod
    def wget_set_timeout(cls, timeout):
        assert isinstance(timeout, int) and timeout>0, timeout
        cls.set_int('wget_timeout', timeout)
    @classmethod
    def wget_get_timeout(cls):
        try:       value = cls.get_int('wget_timeout')
        except: value = 20
        return value
    @classmethod
    def wget_set_triesnum(cls, triesnum):
        assert isinstance(triesnum, int) and triesnum>0, triesnum
        cls.set_int('wget_triesnum', triesnum)
    @classmethod
    def wget_get_triesnum(cls):
        try:       value = cls.get_int('wget_triesnum')
        except: value = 3
        return value
    @classmethod
    def set_default_pane(cls, value):
        cls.set_string('default_pane', value)
    @classmethod
    def get_default_pane(cls):
        try: value = cls.get_string('default_pane')
        except: value = 'SystemSettingPane'
        return value
    @classmethod
    def get_locale(cls):
        import locale
        try:
            value = locale.getdefaultlocale()[0]
            if value: return value # language code and encoding may be None if their values cannot be determined.
            else: return 'en_US'
        except ValueError: # may raise exception: "unknown locale"
            print_traceback()
            return 'en_US'
    @classmethod
    def is_Chinese_locale(cls):
        return cls.get_locale().startswith('zh')
    @classmethod
    def is_Poland_locale(cls):
        return cls.get_locale().startswith('pl')
    @classmethod
    def is_Ubuntu(cls):
        import os
        if not os.path.exists('/etc/lsb-release'): 
            return False
        with open('/etc/lsb-release') as f:
            c = f.read()
        return 'Ubuntu' in c
    @classmethod
    def get_Ubuntu_version(cls):
        '''return 'hardy', 'intrepid', 'jaunty', 'karmic', 'lucid' ...'''
        with open('/etc/lsb-release') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('DISTRIB_CODENAME='):
                return line.split('=')[1].strip()
    @classmethod
    def get_all_Ubuntu_versions(cls):
        return ['hardy', 'intrepid', 'jaunty', 'karmic', 'lucid', 'maverick']
    @classmethod
    def is_Mint(cls):
        import os
        if not os.path.exists('/etc/lsb-release'): return False
        with open('/etc/lsb-release') as f:
            c = f.read()
        return 'LinuxMint' in c
    @classmethod
    def get_Mint_version(cls):
        with open('/etc/lsb-release') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('DISTRIB_RELEASE='):
                a = line.split('=')[1].strip()
        return a
    @classmethod
    def is_YLMF(cls):
        import os
        if not os.path.exists('/etc/lsb-release'): 
            return False
        with open('/etc/lsb-release') as f:
            c = f.read()
        return 'Ylmf_OS' in c
    @classmethod
    def get_YLMF_version(cls):
        '''return 'hardy', 'intrepid', 'jaunty', 'karmic' or 'lucid'.'''
        with open('/etc/lsb-release') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('DISTRIB_CODENAME='):
                return line.split('=')[1].strip()
    @classmethod
    def is_Deepin(cls): # Linux Deepin is based on XUbuntu karmic
        import platform
        return platform.dist()[0] == 'Deepin'
    @classmethod
    def get_Deepin_version(cls):
        'return karmic'
        import platform
        return platform.dist()[2]
    @classmethod
    def is_Fedora(cls):
        import os
        return os.path.exists('/etc/fedora-release')
    @classmethod
    def get_Fedora_version(cls):
        with open('/etc/fedora-release') as f:
            c = f.read()
        return c.split()[2].strip()
    @classmethod
    def is_ArchLinux(cls): # There is no get_arch_version, since ArchLinux has no version.
        import os
        return os.path.exists('/etc/arch-release')
    @classmethod
    def is_GNOME(cls):
        if cls.is_XFCE(): return False
        try:
            get_output('pgrep -u $USER gnome-panel')
            return True
        except:
            return False
    @classmethod
    def is_KDE(cls):
        try:
            get_output('pgrep -u $USER kdeinit')
            return True
        except:
            try:
                get_output('pgrep -u $USER kdeinit4')
                return True
            except: pass
        return False
    @classmethod
    def is_XFCE(cls):
        try:  
            get_output('pgrep -u $USER xfce4-session')
            return True
        except: 
            return False

def set_proxy_string(proxy_string):
    import gnomekeyring
    keyring = gnomekeyring.get_default_keyring_sync()
    id = gnomekeyring.item_create_sync(keyring,
                                       gnomekeyring.ITEM_GENERIC_SECRET,
                                       'ailurus proxy string',
                                       {'appname':'ailurus'},
                                       proxy_string,
                                       True, # update_if_exists
                                      )
    Config.set_proxy_string_id_in_keyring(id)

class UserDeniedError(Exception):
    'User has denied keyring authentication'

def get_proxy_string():
    "Return '', non-empty string or raise exception"
    if hasattr(get_proxy_string, 'denied'): # user has denied access before
        raise UserDeniedError
    
    try:    id = Config.get_proxy_string_id_in_keyring()
    except: return '' # not exist
    
    import gnomekeyring
    keyring = gnomekeyring.get_default_keyring_sync()
    try:
        proxy_string = gnomekeyring.item_get_info_sync(keyring, id).get_secret()
        return proxy_string
    except gnomekeyring.DeniedError: # user denied authentication
        get_proxy_string.denied = True
        raise UserDeniedError

def enable_urllib2_proxy():
    string = get_proxy_string()
    assert string
    import urllib2
    proxy_support = urllib2.ProxyHandler({'http':string}) # FIXME: please support https, ftp, rstp
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

def disable_urllib2_proxy():
    import urllib2
    urllib2.install_opener(None)

def install_locale():
    import gettext
    gettext.translation('ailurus', '/usr/share/locale', fallback=True).install(names=['ngettext'])

def is_legal_license(license):
    return license in [GPL, LGPL, EPL, MPL, BSD, MIT, CDDL, APL, AL] 

def DUAL_LICENSE(A, B):
    assert is_legal_license(A) and is_legal_license(B)
    return _('Dual-licensed under %(A)s and %(B)s') % {'A':A, 'B':B}

def TRI_LICENSE(A, B, C):
    assert is_legal_license(A) and is_legal_license(B) and is_legal_license(C)
    return _('Tri-licensed under %(A)s, %(B)s and %(C)s') % {'A':A, 'B':B, 'C':C}

class ResponseTime:
    map = {}
    changed = False
    @classmethod
    def load(cls):
        import os
        try:
            path = Config.get_config_dir() + 'response_time_2'
            if not os.path.exists(path): return
            with open(path) as f:
                lines = f.readlines()
            for i in range(0, len(lines), 2):
                url = lines[i].strip()
                time = float(lines[i+1].strip())
                cls.map[url] = time
        except IOError:
            print_traceback()
    @classmethod
    def save(cls):
        if not cls.changed: return
        try:
            path = Config.get_config_dir() + 'response_time_2'
            with open(path, 'w') as f:
                for key, value in cls.map.items():
                    print >>f, key
                    print >>f, value
        except IOError:
            print_traceback()
    @classmethod
    def get(cls, url):
        is_string_not_empty(url)
        return cls.map[url]
    @classmethod
    def set(cls, url, value):
        is_string_not_empty(url)
        assert isinstance(value, (int,float)) and value > 0
        cls.map[url] = value
        cls.changed = True

class CommandFailError(Exception):
    'Fail to execute a command'

def run(command, ignore_error=False):
    is_string_not_empty(command)
    if not isinstance(ignore_error,  bool): raise TypeError

    if getattr(run, 'terminal', None):
        assert run.terminal.__class__.__name__ == 'Terminal'
        try:
            run.terminal.run(command)
        except CommandFailError:
            if not ignore_error: raise
    else:
        print '\x1b[1;33m', _('Run command:'), command, '\x1b[m'
        import os, subprocess
        env = None
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
        task = subprocess.Popen(command, env=env, shell=True)
        task.wait()
        if task.returncode and ignore_error == False:
            raise CommandFailError(command, task.returncode)

def pack(D):
    assert isinstance(D, dict)
    import StringIO
    buf = StringIO.StringIO()
    for k,v in D.items():
        print >>buf, k
        print >>buf, v
    return buf.getvalue()

def packed_env_string():
    import os
    env = dict( os.environ )
    env['PWD'] = os.getcwd()
    return pack(env)

def get_dbus_daemon_version():
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    ret = obj.get_version(dbus_interface='cn.ailurus.Interface')
    return ret    

def restart_dbus_daemon():
    authenticate()
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    obj.exit(dbus_interface='cn.ailurus.Interface')

def get_authentication_method():
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    ret = obj.get_check_permission_method(dbus_interface='cn.ailurus.Interface')
    ret = int(ret)
    assert ret == 0 or ret == 1, ret
    return ret

def authenticate():
    if get_authentication_method() == 0:
        import dbus
        bus = dbus.SessionBus()
        policykit = bus.get_object('org.freedesktop.PolicyKit.AuthenticationAgent', '/')
        import os
        policykit.ObtainAuthorization('cn.ailurus', dbus.UInt32(0), dbus.UInt32(os.getpid()))

def spawn_as_root(command):
    is_string_not_empty(command)
    
    authenticate()
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    obj.spawn(command, packed_env_string(), secret_key, dbus_interface='cn.ailurus.Interface')

def drop_priviledge():
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    obj.drop_priviledge(secret_key, dbus_interface='cn.ailurus.Interface')
    
class AccessDeniedError(Exception):
    'User press cancel button in policykit window'

def run_as_root(cmd, ignore_error=False):
    is_string_not_empty(cmd)
    assert isinstance(ignore_error, bool)
    
    import os
    if os.getuid()==0:
        run(cmd, ignore_error)
        return
    
    print '\x1b[1;33m', _('Run command:'), cmd, '\x1b[m'
    authenticate()
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    try:
        obj.run(cmd, packed_env_string(), secret_key, ignore_error, timeout=36000, dbus_interface='cn.ailurus.Interface')
    except dbus.exceptions.DBusException, e:
        if e.get_dbus_name() == 'cn.ailurus.AccessDeniedError': raise AccessDeniedError(*e.args)
        else: raise

def is_string_not_empty(string):
    if type(string)!=str and type(string)!=unicode: raise TypeError(string)
    if string=='': raise ValueError

def get_output(cmd, ignore_error=False):
    is_string_not_empty(cmd)
    assert isinstance(ignore_error, bool)
    
    import commands
    status, output=commands.getstatusoutput(cmd)
    if status and not ignore_error: raise CommandFailError(cmd)
    return output
    
class TempOwn:
    def __init__(self,path):
        is_string_not_empty(path)
        if path[0]=='-':
            raise ValueError
        import os
        dirname = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(dirname):
            run_as_root('mkdir "%s"'%dirname)
        if not os.path.exists(path):
            run_as_root('touch "%s"'%path)
        run_as_root('chown $USER:$USER %s'%path )
        self.path = path
    def __enter__(self):
        return None
    def __exit__(self, type, value, traceback):
        run_as_root('chown root:root %s'%self.path)

def notify(title, content):
    'Show a notification in the right-upper corner.'
    # title must not be empty. 
    # otherwise, this error happens. notify_notification_update: assertion `summary != NULL && *summary != '\0'' failed
    assert isinstance(title, str) and title
    assert isinstance(content, str)
    try:
        import pynotify
        if not hasattr(notify,'ailurus_notify'):
            notify.ailurus_notify = pynotify.Notification(' ',' ')
        icon = D+'suyun_icons/notify-icon.png'
        if title == notify.ailurus_notify.get_property('summary'):
            notify.ailurus_notify = pynotify.Notification(title, content, icon)
            notify.ailurus_notify.set_hint_string("x-canonical-append", "")
        else:
            notify.ailurus_notify.update(title, content, icon)
               
        notify.ailurus_notify.set_timeout(10000)
        notify.ailurus_notify.show()
    except:
        print_traceback()

def is32():
    import os
    return os.uname()[-1] != 'x86_64'

def file_contain(path, *lines):
    'Return True if the file contains all the lines'
    is_string_not_empty(path)
    if not len(lines): raise ValueError
    for line in lines:
        is_string_not_empty(line)
    import os
    if os.path.exists(path):
        with open(path, 'r') as f:
            contents = f.readlines()
        for line in lines:
            if line[-1]!='\n': line+='\n'
            if not line in contents: return False
        return True
    return False

def file_insert(path, *args):
    'Insert lines into file. The format of args is "position, line, position, line..."'
    is_string_not_empty(path)
    if not len(args): raise ValueError
    for i in range(0, len(args), 2):
        if type(args[i])!=int: raise TypeError
        is_string_not_empty(args[i+1])
    
    import os
    if not os.path.exists(path):
        run('touch %s'%path)
    with open(path, "r") as f:
        contents = f.readlines()
    for i in range(0, len(args), 2):
        line = args[i]
        string = args[i+1]
        if string[-1]!='\n': string+='\n'
        contents.insert(line, string)
    with open(path, "w") as f:
        f.writelines(contents)

def file_append(path, *lines):
    is_string_not_empty(path)
    if not len(lines): raise ValueError
    for line in lines:
        is_string_not_empty(line)
    with open(path, 'a') as f:
        for line in lines:
            if line[-1]!='\n': line+='\n'
            f.write(line)

def file_remove(path, *lines):
    is_string_not_empty(path)
    if not len(lines): raise ValueError
    for line in lines:
        is_string_not_empty(line)
    with open(path, "r") as f:
        contents = f.readlines()
    for line in lines:
        if line[-1]!='\n': line+='\n'
        try: 
            contents.remove(line)
        except ValueError: pass
    with open(path, "w") as f:
        f.writelines(contents)

def free_space(path):
    is_string_not_empty(path)
    assert path[0]=='/'
    import os, statvfs
    e = os.statvfs(path)
    return e[statvfs.F_BAVAIL] * e[statvfs.F_BSIZE]

def own_by_user(*paths):
    if not len(paths): raise ValueError
    for path in paths:
        is_string_not_empty(path)
        if path[0]=='-': raise ValueError
    for path in paths:
        import os
        if os.stat(path).st_uid != os.getuid():
            run_as_root('chown $USER:$USER "%s"'%path)

def is_pkg_list(packages):
    if not len(packages): raise ValueError
    for package in packages:
        is_string_not_empty(package)
        if package[0]=='-': raise ValueError
        if ' ' in package: raise ValueError

def run_as_root_in_terminal(command):
    is_string_not_empty(command)
    print '\x1b[1;33m', _('Run command:'), command, '\x1b[m'

    import tempfile
    t = tempfile.NamedTemporaryFile('w')
    t.write(command)
    t.flush()
    string = 'LANG=C xterm -T "Ailurus Terminal" -e bash %s' % t.name

    authenticate()
    import dbus
    bus = dbus.SystemBus()
    obj = bus.get_object('cn.ailurus', '/')
    try:
        obj.run(string, packed_env_string(), secret_key, False, timeout=36000, dbus_interface='cn.ailurus.Interface')
    except dbus.exceptions.DBusException, e:
        if e.get_dbus_name() == 'cn.ailurus.AccessDeniedError': raise AccessDeniedError(*e.args)
        else: raise

class RPM:
    fresh_cache = False
    __set1 = set() # __set1 consists of all installed software
    __set2 = set() # __set2 = __set1 + all available software
    @classmethod
    def cache_changed(cls):
        cls.fresh_cache = False
    @classmethod
    def refresh_cache(cls):
        if cls.fresh_cache: return
        cls.fresh_cache = True
        cls.__set1 = set()
        cls.__set2 = set()
        import subprocess, os
        path = os.path.dirname(os.path.abspath(__file__)) + '/support/dump_rpm_installed.py'
        task = subprocess.Popen(['python', path],
            stdout=subprocess.PIPE,
            )
        for line in task.stdout:
            cls.__set1.add(line.strip())
        task.wait()
        path = os.path.dirname(os.path.abspath(__file__)) + '/support/dump_rpm_existing_new.py'
        task = subprocess.Popen(['python', path],
            stdout=subprocess.PIPE,
            )
        for line in task.stdout:
            cls.__set2.add(line.strip())
        task.wait()
    @classmethod
    def get_installed_pkgs_set(cls):
        cls.refresh_cache()
        return cls.__set1
    @classmethod
    def get_existing_pkgs_set(cls):
        cls.refresh_cache()
        return cls.__set2
    @classmethod
    def exist(cls, package_name):
        cls.refresh_cache()
        return package_name in cls.__set1 or package_name in cls.__set2
    @classmethod
    def installed(cls, package_name):
        is_pkg_list([package_name])
        cls.refresh_cache()
        return package_name in cls.__set1
    @classmethod
    def install(cls, *package):
        run_as_root_in_terminal('yum install %s -y' % ' '.join(package))
        cls.cache_changed()
    @classmethod
    def install_local(cls, path):
        assert isinstance(path, str)
        import os
        assert os.path.exists(path)
        run_as_root_in_terminal('yum localinstall --nogpgcheck -y %s' % path)
        cls.cache_changed()
    @classmethod
    def remove(cls, *package):
        run_as_root_in_terminal('yum remove %s -y' % ' '.join(package))
        cls.cache_changed()
    @classmethod
    def import_key(cls, path):
        assert isinstance(path, str)
        run_as_root_in_terminal('rpm --import %s' % path)

class APT:
    fresh_cache = False
    apt_get_update_is_called = False
    installed_set = set()
    avail_set = set()
    @classmethod
    def cache_changed(cls):
        cls.fresh_cache = False
    @classmethod
    def refresh_cache(cls):
        if cls.fresh_cache: return
        cls.fresh_cache = True
        cls.installed_set.clear()
        cls.avail_set.clear()
        import subprocess, os
        path = os.path.dirname(os.path.abspath(__file__))+'/support/dump_deb_installed.py'
        task = subprocess.Popen(['python', path], stdout=subprocess.PIPE)
        for line in task.stdout:
            cls.installed_set.add(line.rstrip())
        task.wait()
        path = os.path.dirname(os.path.abspath(__file__))+'/support/dump_deb_existing.py'
        task = subprocess.Popen(['python', path], stdout=subprocess.PIPE)
        for line in task.stdout:
            cls.avail_set.add(line.rstrip())
        task.wait()
    @classmethod
    def get_installed_pkgs_set(cls):
        cls.refresh_cache()
        return cls.installed_set
    @classmethod
    def get_existing_pkgs_set(cls):
        cls.refresh_cache()
        return cls.avail_set
    @classmethod
    def get_autoremovable_pkgs(cls):
        ret = []
        import subprocess, os
        path = os.path.dirname(os.path.abspath(__file__))+'/support/dump_apt_autoremovable.py'
        task = subprocess.Popen(['python', path], stdout=subprocess.PIPE)
        class EndOfStream:
            pass
        def readline(stream):
            line = stream.readline()
            if len(line) == 0: raise EndOfStream
            return line.strip()
        try:
            while True:
                name = readline(task.stdout)
                size = readline(task.stdout)
                size = long(size)
                summary = readline(task.stdout)
                ret.append([name, size, summary,])
        except EndOfStream:
            pass
        task.wait()
        return ret
    @classmethod
    def installed(cls, package_name):
        is_pkg_list([package_name])
        cls.refresh_cache()
        return package_name in cls.installed_set
    @classmethod
    def exist(cls, package_name):
        is_pkg_list([package_name])
        cls.refresh_cache()
        return package_name in cls.installed_set or package_name in cls.avail_set
    @classmethod
    def install(cls, *packages):
        is_pkg_list(packages)
        if cls.apt_get_update_is_called == False:
            cls.apt_get_update()
        print '\x1b[1;32m', _('Installing packages:'), ' '.join(packages), '\x1b[m'
        # use "force-yes" because playonlinux repository has no gpg key, we want to install it without key.
        run_as_root_in_terminal('apt-get install -y --force-yes ' + ' '.join(packages))
        APT.cache_changed()
    @classmethod
    def remove(cls, *packages):
        is_pkg_list(packages)
        print '\x1b[1;31m', _('Removing packages:'), ' '.join(packages), '\x1b[m'
        packages = [p for p in packages if APT.installed(p)]
        run_as_root_in_terminal('apt-get remove -y ' + ' '.join(packages))
        APT.cache_changed()
    @classmethod
    def neet_to_run_apt_get_update(cls):
        cls.apt_get_update_is_called = False
    @classmethod
    def apt_get_update(cls):
        # (c) 2005-2007 Canonical, GPL
        print '\x1b[1;36m', _('Run "apt-get update". Please wait for few minutes.'), '\x1b[m'
        run_as_root_in_terminal('apt-get update')
        cls.apt_get_update_is_called = True
        cls.cache_changed()
    @classmethod
    def install_local(cls, *packages):
        for package in packages:
            if VERSION>='lucid': # -n == non-interactive
                run_as_root('gdebi-gtk -n --auto-close %s' % package)
            else:
                run_as_root('gdebi-gtk -n %s' % package)
        cls.cache_changed()

class PACMAN:
    fresh_cache = False
    pacman_sync_called = False
    __pkgs = set()
    __allpkgs = set()
    @classmethod
    def cache_changed(cls):
        cls.fresh_cache = False
    @classmethod
    def refresh_cache(cls):
        if getattr(cls, 'fresh_cache', False): return
        cls.fresh_cache = True
        cls.__pkgs = set()
        cls.__allpkgs = set()
        import subprocess, os
        #get installed package names
        task = subprocess.Popen(['pacman', '-Q'],
            stdout=subprocess.PIPE,
            )
        for line in task.stdout:
            cls.__pkgs.add(line.split()[0])
        task.wait()
        #get all existing package names
        task = subprocess.Popen(['pacman', '-Sl'],
            stdout=subprocess.PIPE,
            )
        for line in task.stdout:
            cls.__allpkgs.add(line.split()[1])
        task.wait()
    @classmethod
    def get_existing_pkgs_set(cls):
        cls.refresh_cache()
        return cls.__allpkgs
    @classmethod
    def installed(cls, package_name):
        is_pkg_list([package_name])
        cls.refresh_cache()
        return package_name in cls.__pkgs
    @classmethod
    def exist(cls, package_name):
        cls.refresh_cache()
        return package_name in cls.__pkgs or package_name in cls.__allpkgs
    @classmethod
    def install(cls, *packages):
        is_pkg_list(packages)
        if not cls.pacman_sync_called:
            cls.pacman_sync()
        print '\x1b[1;32m', _('Installing packages:'), ' '.join(packages), '\x1b[m'
        run_as_root_in_terminal('pacman -S --noconfirm %s' % ' '.join(packages))
        cls.cache_changed()
    @classmethod
    def install_local(cls, path):
        assert isinstance(path, str)
        import os
        assert os.path.exists(path)
        run_as_root_in_terminal('pacman -U --noconfirm %s' % path)
        cls.cache_changed()
    @classmethod
    def remove(cls, *packages):
        is_pkg_list(packages)
        print '\x1b[1;31m', _('Removing packages:'), ' '.join(packages), '\x1b[m'
        packages = [p for p in packages if PACMAN.installed(p)]
        run_as_root_in_terminal('pacman -R --noconfirm %s' % ' '.join(packages))
        cls.cache_changed()
    @classmethod
    def pacman_sync(cls):
        print '\x1b[1;36m', _('Run "pacman -Sy". Please wait for a few minutes.'), '\x1b[m'
        run_as_root_in_terminal('pacman -Sy')
        cls.pacman_sync_called = True

def get_response_time(url):
    is_string_not_empty(url)

    import urllib2
    import time
    import sys
    begin = time.time()
    if sys.version_info[:2]>(2,5): # for python 2.6+
        urllib2.urlopen(url, timeout=3)
    else: # for python 2.5
        urllib2.urlopen(url) # FIXME: no timeout!
    end = time.time()
    return (end - begin) * 1000 # in milliseconds

def derive_size(size):
    if not ( isinstance(size, int) or isinstance(size, long) ): raise TypeError
    if not size>=0: raise ValueError
    _1G = 1e9
    _1M = 1e6
    _1K = 1e3
    if size>=_1G:
        return _('%.1f GB') % ( size/_1G )
    if size>=_1M:
        return _('%.1f MB') % ( size/_1M )
    if size>=_1K:
        return _('%.1f KB') % ( size/_1K )
    return _('%s bytes') % int(size)

def derive_time(time):
    if not isinstance(time, int): raise TypeError
    if not time>=0: raise ValueError
    _1h = 3600.
    _1m = 60.
    if time >= _1h:
        return _('%.1f hours') % ( time/_1h )
    if time >= _1m:
        return _('%.1f minutes') % ( time/_1m )
    return _('%d seconds') % time

class KillWhenExit:
    task_list = []
    @classmethod
    def add(cls, task):
        import subprocess
        if not isinstance(task, (str, unicode, subprocess.Popen)): raise TypeError
        if isinstance(task, (str, unicode)):
            assert task!=''
            print '\x1b[1;33m', _('Run command:'), task, '\x1b[m' 
            task=subprocess.Popen(task, shell=True)
        cls.task_list.append(task)
    @classmethod
    def kill_all(cls):
        for task in cls.task_list:
            try:
                import os, signal
                os.kill(task.pid, signal.SIGTERM)
            except:
                print_traceback()
        cls.task_list = []

def download(url, filename):
    is_string_not_empty(url)
    assert url[0]!='-'
    is_string_not_empty(filename)
    assert filename[0]!='-'
    timeout = Config.wget_get_timeout()
    tries = Config.wget_get_triesnum()
    try:
        run("wget --timeout=%(timeout)s --tries=%(tries)s '%(url)s' -O '%(filename)s'"
            %{'timeout':timeout, 'tries':tries, 'url':url, 'filename':filename} )
    except:
        import os
        if os.path.exists(filename): os.unlink(filename)
        raise
    
def reset_dir():
    import os, sys
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

class APTSource2:
    re_pattern_server = None
    re_pattern_url = None
    @classmethod
    def all_conf_files(cls):
        import glob, os
        ret = glob.glob('/etc/apt/sources.list.d/*.list')
        if os.path.exists('/etc/apt/sources.list'):
            ret.append('/etc/apt/sources.list')
        return ret
    @classmethod
    def iter_all_lines(cls):
        for file in cls.all_conf_files():
            f = open(file)
            for line in f:
                if not line.endswith('\n'): line += '\n'
                yield line
            f.close()
    @classmethod
    def all_lines(cls):
        return [line for line in cls.iter_all_lines()]
    @classmethod
    def all_lines_contain(cls, snip):
        snip = cls.remove_comment(snip)
        for line in cls.iter_all_lines():
            if snip in line: return True
        return False
    @classmethod
    def all_lines_contain_all_of(cls, many_snips):
        for snip in many_snips:
            if not cls.all_lines_contain(snip): return False
        return True
    @classmethod
    def add_lines_to_file(cls, lines, file_path = '/etc/apt/sources.list'):
        assert isinstance(lines, list)
        assert isinstance(file_path, str)
        
        with TempOwn(file_path) as o:
            with open(file_path) as f:
                contents = f.readlines()
            if len(contents) and not contents[-1].endswith('\n'):
                contents.append('\n')
            contents.extend(lines)
            with open(file_path, 'w') as f:
                f.writelines(contents)
    @classmethod
    def remove_snips_from(cls, snips, file_path):
        assert isinstance(snips, list)
        assert isinstance(file_path, str)
        
        with open(file_path) as f:
            contents = f.readlines()
        changed = False
        for i, line in enumerate(contents):
            line = cls.remove_comment(line)
            for snip in snips:
                snip = cls.remove_comment(snip)
                if snip in cls.remove_comment(line):
                    contents[i] = ''
                    changed = True
                    break
        if changed:
            with TempOwn(file_path) as o:
                with open(file_path, 'w') as f:
                    f.writelines(contents)
    @classmethod
    def remove_snips_from_all_files(cls, snips):
        assert isinstance(snips, list)
        for file_path in cls.all_conf_files():
            cls.remove_snips_from(snips, file_path)
    @classmethod
    def remove_comment(cls, line):
        return line.split('#', 1)[0].strip()
    @classmethod
    def is_official_line(cls, line):
        line = cls.remove_comment(line)
        for snip in ['-backports', '-proposed', '-security', '-updates']:
            snip = VERSION + snip
            if snip in line: return True
        return False
    @classmethod
    def get_server_from_line(cls, line):
        line = cls.remove_comment(line)
        import re
        if cls.re_pattern_server is None:
            cls.re_pattern_server = re.compile(r'^deb(-src)? [a-z]+://([^/]+)/.*$')
        match = cls.re_pattern_server.match(line)
        if match: return match.group(2)
        else:     return None
    @classmethod
    def get_url_from_line(cls, line):
        line = cls.remove_comment(line)
        import re
        if cls.re_pattern_url is None:
            cls.re_pattern_url = re.compile(r'^deb(-src)? (\S+) .*$')
        match = cls.re_pattern_url.match(line)
        if match: return match.group(2)
        else:     return None
    @classmethod
    def official_servers(cls):
        ret = set()
        for line in cls.iter_all_lines():
            if cls.is_official_line(line):
                server = cls.get_server_from_line(line)
                ret.add(server)
        return ret
    @classmethod
    def official_urls(cls):
        ret = set()
        for line in cls.iter_all_lines():
            if cls.is_official_line(line):
                url = cls.get_url_from_line(line)
                ret.add(url)
        return ret
    @classmethod
    def third_party_urls(cls):
        offi_urls = cls.official_urls()
        ret = set()
        for line in cls.iter_all_lines():
            url = cls.get_url_from_line(line)
            if url and url not in offi_urls: ret.add(url)
        return ret
    @classmethod
    def all_urls(cls):
        ret = set()
        for line in cls.iter_all_lines():
            url = cls.get_url_from_line(line)
            if url: ret.add(url)
        return ret
    @classmethod
    def this_line_contain(cls, line, snip):
        return snip in cls.remove_comment(line)
    @classmethod
    def this_line_contain_any_of(cls, line, snip_set):
        for snip in snip_set:
            if cls.this_line_contain(line, snip):
                return True
        return False
    @classmethod
    def remove_official_servers(cls):
        offi_servers = cls.official_servers()
        for file in cls.all_conf_files():
            with open(file) as f:
                contents = f.readlines()
            changed = False
            for i, line in enumerate(contents):
                if cls.this_line_contain_any_of(line, offi_servers):
                    contents[i] = ''
                    changed = True
            if changed:
                with TempOwn(file) as o:
                    with open(file, 'w') as f:
                        f.writelines(contents)
    @classmethod
    def add_official_url(cls, url):
        with TempOwn('/etc/apt/sources.list') as o:
            with open('/etc/apt/sources.list') as f:
                contents = f.readlines()
            if len(contents) and not contents[-1].endswith('\n'):
                contents.append('\n')
            contents.append('deb %(url)s %(version)s main restricted universe multiverse\n'
                            'deb %(url)s %(version)s-backports restricted universe multiverse\n'
                            'deb %(url)s %(version)s-proposed main restricted universe multiverse\n'
                            'deb %(url)s %(version)s-security main restricted universe multiverse\n'
                            'deb %(url)s %(version)s-updates main restricted universe multiverse\n'
                            'deb-src %(url)s %(version)s main restricted universe multiverse\n'
                            'deb-src %(url)s %(version)s-backports main restricted universe multiverse\n'
                            'deb-src %(url)s %(version)s-proposed main restricted universe multiverse\n'
                            'deb-src %(url)s %(version)s-security main restricted universe multiverse\n'
                            'deb-src %(url)s %(version)s-updates main restricted universe multiverse\n'
                            % {'url':url, 'version':VERSION})
            with open('/etc/apt/sources.list', 'w') as f:
                f.writelines(contents)

import threading
class PingThread(threading.Thread):
    def __init__(self, url, server, result):
        is_string_not_empty(url)
        is_string_not_empty(server)
        assert isinstance(result, list)
        
        threading.Thread.__init__(self)
        self.url = url
        self.server = server
        self.result = result
        import time
        self.start_time = time.time()
    def elapsed_time(self):
        import time
        return time.time() - self.start_time
    def run(self):
        try:
            time = get_response_time(self.url)
            self.result.append([self.server, time])
        except:
            self.result.append([self.server, 'unreachable'])

def open_web_page(page):
    is_string_not_empty(page)
    notify( _('Opening web page'), page)
    KillWhenExit.add('xdg-open %s'%page)

def report_bug(*w):
    page = 'http://code.google.com/p/ailurus/issues/entry'
    notify( _('Opening web page'), page)
    KillWhenExit.add('xdg-open %s'%page)

import os
class firefox:
    support = False # do not use this class if support is False
    preference_dir = None # form: ~/.mozilla/firefox/5y7bqw54.default/
    extensions_dir = None # form: preference_dir + 'extensions/'
    prefs_js_path = None # form: preference_dir + 'prefs.js'
    pattern1 = None # regexp
    pattern2 = None # regexp
    prefs_js_line_pattern = None
    key2value = {} # key is native python constant. value is native python constant.
    key2line = {} # key is native python constant. line is the line in prefs.js
    @classmethod
    def init(cls):
        'may raise exception'
        ini_file = os.path.expanduser('~/.mozilla/firefox/profiles.ini')
        with open(ini_file) as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line == 'Name=default\n': break
        else:
            raise Exception('"Name=default" not found')
        lines = lines[i+1:]
        for line in lines:
            if line.startswith('Path='):
                dir_name = line.split('=', 1)[1].strip()
                break
        else:
            raise Exception('"Path=..." not found')
        cls.preference_dir = os.path.expanduser('~/.mozilla/firefox/') + dir_name + '/'
        assert os.path.exists(cls.preference_dir), cls.preference_dir
        cls.extensions_dir = cls.preference_dir + 'extensions/'
        if not os.path.exists(cls.extensions_dir): os.mkdir(cls.extensions_dir)
        cls.prefs_js_path = cls.preference_dir + 'prefs.js'
        if not os.path.exists(cls.prefs_js_path): # touch file
            with open(cls.prefs_js_path, 'w') as f: pass
        import re
        cls.pattern1 = re.compile('em:name="(.+)"')
        cls.pattern2 = re.compile('<em:name>(.+)</em:name>')
        cls.prefs_js_line_pattern = re.compile(r'''^user_pref\( # begin
            (['"][^'"]+['"]) # key
            ,\s
            (.+) # value
            \); # end ''', re.VERBOSE)
        cls.load_user_prefs()
        cls.support = True
    @classmethod
    def is_extension_archive(cls, file_path):
        assert isinstance(file_path, str) and file_path
        assert file_path.endswith('.xpi') or file_path.endswith('.jar')
    @classmethod
    def install_extension_archive(cls, file_path):
        cls.is_extension_archive(file_path)
        print '\x1b[1;33m', _('Run command:'), 'cp %s %s' % (file_path, cls.extensions_dir), '\x1b[m'
        import shutil
        shutil.copy(file_path, cls.extensions_dir)
    @classmethod
    def extension_archive_exists(cls, file_path):
        cls.is_extension_archive(file_path)
        return os.path.exists(cls.extensions_dir + file_path)
    @classmethod
    def remove_extension_archive(cls, file_path):
        cls.is_extension_archive(file_path)
        print '\x1b[1;33m', _('Run command:'), 'rm -f %s%s' % (cls.extensions_dir, file_path), '\x1b[m'
        os.unlink(cls.extensions_dir + file_path)
    @classmethod
    def extension_is_installed(cls, extension_name):
        assert isinstance(extension_name, (str, unicode)) and extension_name
        import glob
        dirs = glob.glob(cls.extensions_dir + '*')
        ret = []
        for dir in dirs:
            if extension_name == cls.get_extension_name_in(dir):
                return True
        return False
    @classmethod
    def all_installed_extensions(cls):
        import glob
        dirs = glob.glob(cls.extensions_dir + '*')
        ret = []
        for dir in dirs:
            ret.append(cls.get_extension_name_in(dir))
        return ret
    @classmethod
    def get_extension_name_in(cls, dir):
        assert isinstance(dir, str) and dir
        rdf_file = '%s/install.rdf' % dir
        if not os.path.exists(rdf_file): return None
        with open(rdf_file) as f:
            content = f.read()
        return cls.guess_name_from_content_method1(content) or cls.guess_name_from_content_method2(content)  
    @classmethod
    def guess_name_from_content_method1(cls, content):
        try:    return cls.pattern1.search(content).group(1)
        except: return None
    @classmethod
    def guess_name_from_content_method2(cls, content):
        try:    return cls.pattern2.search(content).group(1)
        except: return None
    @classmethod
    def all_user_pref_lines(cls, content):
        assert isinstance(content, (str, unicode))
        lines = content.splitlines()
        ret = []
        for line in lines:
            if line.startswith('user_pref(') and line.endswith(');'):
                ret.append(line)
        return ret
    @classmethod
    def get_key_value_from(cls, user_pref_line): # may raise exception
        'return (key, value). both of them are native python constant.'
        assert isinstance(user_pref_line, (str, unicode))
        match = cls.prefs_js_line_pattern.match(user_pref_line)
        assert match, user_pref_line
        key = match.group(1)
        key = eval(key)
        value = match.group(2)
        true = True # javascript boolean
        false = False # javascript boolean
        value = eval(value)
        return key, value
    @classmethod
    def load_user_prefs(cls):
        cls.key2value.clear()
        with open(cls.prefs_js_path) as f:
            content = f.read()
        lines = cls.all_user_pref_lines(content)
        for line in lines:
            try:
                key, value = cls.get_key_value_from(line)
                cls.key2value[key] = value
                cls.key2line[key] = line
            except:
                print_traceback()
    @classmethod
    def get_pref(cls, key):
        'key should be native python string. return native python constant'
        assert isinstance(key, (str, unicode))
        return cls.key2value[key]
    @classmethod
    def set_pref(cls, key, value):
        'value should be native python variable'
        cls.key2value[key] = value
        repr_key = '"%s"' % key
        repr_value = repr(value)
        if value == True: repr_value = 'true'
        elif value == False: repr_value = 'false'
        cls.key2line[key] = 'user_pref(%s, %s);' % (repr_key, repr_value)
    @classmethod
    def remove_pref(cls, key):
        try: del cls.key2value[key]
        except KeyError: pass
    @classmethod
    def save_user_prefs(cls):
        keys = cls.key2value.keys()
        keys.sort()
        with open(cls.prefs_js_path, 'w') as f:
            for key in keys:
                line = cls.key2line[key]
                print >>f, line

def delay_notify_firefox_restart(show_notify=False):
    assert isinstance(show_notify, bool)
    if not show_notify:
        delay_notify_firefox_restart.should_show = True
    else:
        if getattr(delay_notify_firefox_restart, 'should_show', False):
            delay_notify_firefox_restart.should_show = False
            try:
                string = get_output('ps -a -u $USER | grep firefox', True)
                if string:
                    notify(_('Please restart Firefox'), _('Please restart Firefox to complete installation.'))
                else:
                    KillWhenExit.add('firefox')
            except:
                print_traceback()

def sha1(path):
    is_string_not_empty(path)
    import os
    assert os.path.exists(path)
    import hashlib
    obj = hashlib.sha1()
    f = open(path)
    while True:
        block = f.read(4096)
        if len(block)==0: break
        obj.update(block)
    f.close()
    return obj.hexdigest()

class R:
    pingtime_cache = {}
    @classmethod
    def get_speed(cls, url):
        assert url and isinstance(url, str)
        import re
        match = re.match('^\w+://([^/]+)/.+$', url)
        assert match, url
        try:
            server = match.group(1)
            if server in cls.pingtime_cache:
                Time = cls.pingtime_cache[server]
            else:
                Time = get_response_time(url)
                print _('Response time of server %(name)s is %(time).1f ms.') % {'name':server, 'time':Time}
        except:
            print _('Server %s does not respond.')%server
            Time = 10000.0
        finally:
            cls.pingtime_cache[server] = Time
            return Time
    @staticmethod
    def compare(u1, u2):
        s1 = R.get_speed(u1)
        s2 = R.get_speed(u2)
        return cmp(s1, s2)
    def sort(self):
        if self.sorted: return
        self.sorted = True
        
        if isinstance(self.url, str): 
            self.sorted_url = [self.url]
        elif isinstance(self.url, list):
            if len(self.url)>1:
                self.url.sort(R.compare)
            self.sorted_url = self.url
        else:
            raise Exception
    def delete_duplicate(self, List):
        ret = []
        servers = set()
        for url in List:
            import re
            match = re.search('://([^/]+)/', url)
            server = match.group(1)
            if not server in servers:
                ret.append(url)
                servers.add(server)
        return ret
    def __init__(self, url_list, size=None, hash=None, filename=None):
        #check url
        assert url_list
        assert isinstance(url_list, (str,list))
        if isinstance(url_list, str): 
            url_list = [ url_list ]
        for e in url_list:
            assert isinstance(e, str), e
            assert e.startswith('http://') or e.startswith('https://') or e.startswith('ftp://')
        #check size
        if size!=None:
            assert size>0
            assert isinstance(size, int) or isinstance(size, long), size
        #check hash
        if hash:
            assert isinstance(hash, str), hash
            assert len(hash)==40, hash

        self.url = self.delete_duplicate(url_list)
        self.size = size
        self.hash = hash
        if filename:
            self.filename = filename
        else:
            if isinstance(url_list, str): u = url_list
            elif isinstance(url_list, list): u = url_list[0]
            import re
            self.filename = re.match('^.+/(.+)$', u).group(1)
            
        self.sorted = False
    def can_download(self):
        import urllib2
        for url in self.url:
            try:
                print url
                f = urllib2.urlopen(url)
                return True
            except:
                pass
        return False
    @classmethod
    def create_tmp_dir(cls):
        dir = '/var/cache/ailurus/'
        import os
        if not os.path.exists(dir):
            run_as_root('mkdir %s -p'%dir)
        own_by_user(dir)
    def check(self, path):
        if self.size:
            import os
            filesize=os.path.getsize(path)
            if filesize!=self.size: 
                raise CommandFailError('File is broken. Expected file length is %s, but real length is %s.'%(self.size, filesize) )
        if self.hash:
            print _('Checking file integrity ...'),
            filehash = sha1(path)
            if filehash!=self.hash: 
                raise CommandFailError('File is broken. Expected hash is %s, but real hash is %s.'%(self.hash, filehash) )
            print _('Good.')
    def download(self):
        self.sort()
        dest = '/var/cache/ailurus/'+self.filename
        import os, sys
        assert isinstance(self.sorted_url, list)
        for i, url in enumerate(self.sorted_url):
            print '\x1b[1;36m', _('Using mirror %(i)s. There are a total of %(total)s mirrors.') % {'i' : i+1, 'total' : len(self.sorted_url)}, '\x1b[m'
            assert isinstance(url, str)
            try:
                R.create_tmp_dir()
                download(url, dest)
                self.check(dest)
                return dest
            except:
                print_traceback()
        
        raise CommandFailError(self.url)

class ETCEnvironment:
    def __init__(self):
        self.keys = []
        self.values = {}
        f = open('/etc/environment')
        for line in f:
            items = line.split('=',1)
            if len(items)<2: continue
            key = items[0].strip()
            if not key in self.keys:
                self.keys.append(key)
            value = items[1].strip()
            if value[0]==value[-1]=='\'' or value[0]==value[-1]=='\"': value = value[1:-1]
            self.values[key] = value.split(':')
    def add(self, key, *values):
        assert key and isinstance(key, str),    key
        
        values = list(values)
        assert values
        for v in values:
            assert v and isinstance(v, str),    v
            assert not ':' in v,     v
        
        if not key in self.keys:
            self.keys.append(key)
            self.values[key] = values
        else:
            self.values[key] = values+self.values[key]
    def remove(self, key, *values):
        assert key and isinstance(key, str),    key
        for v in values:
            assert v and isinstance(v, str),    v
            assert not ':' in v,     v

        if not key in self.keys: return
        if not values: 
            # delete it directly
            try:    self.keys.remove(key)
            except: pass
            try:    del self.values[key]
            except: pass
        else:
            List = self.values[key]
            self.values[key] = [e for e in List if not e in values]
    def save(self):
        with TempOwn('/etc/environment') as o:
            f = open('/etc/environment', 'w')
            for key in self.keys:
                if not self.values[key]: continue
                f.write(key)
                f.write('=')
                f.write('\"')
                f.write(':'.join(self.values[key]))
                f.write('\"')
                f.write('\n')

class Chdir:
    def __init__(self,path):
        is_string_not_empty(path)
        if path[0]=='-':
            raise ValueError
        import os
        if not os.path.exists(path):
            raise ValueError
        
        self.oldpath = os.getcwd()
        os.chdir(path)
    def __enter__(self):
        return None
    def __exit__(self, type, value, traceback):
        import os
        os.chdir(self.oldpath)

def create_file(path, content):
    with TempOwn(path) as o:
        with open(path, 'w') as f:
            f.write(content)

def print_traceback():
    import sys, traceback
    traceback.print_exc(file = sys.stderr)

class Tasksel:
    fresh_cache = False
    set1 = set()
    set2 = set()
    @classmethod
    def cache_changed(cls):
        cls.fresh_cache = False
    @classmethod
    def refresh_cache(cls):
        if cls.fresh_cache: return
        cls.fresh_cache = True
        cls.set1 = set()
        cls.set2 = set()
        s = get_output('tasksel --list-tasks', ignore_error=True)
        for line in s.split('\n'):
            if len(line) == 0: break
            name = line.split()[1]
            if line[0] == 'i':
                cls.set1.add(name)
            elif line[0] == 'u':
                cls.set2.add(name)
    @classmethod
    def install_tasksel_package(cls):
        if not APT.installed('tasksel'):
            APT.install('tasksel')
    @classmethod
    def installed(cls, name):
        is_string_not_empty(name)
        cls.refresh_cache()
        return name in cls.set1
    @classmethod
    def exists(cls, name):
        is_string_not_empty(name)
        cls.refresh_cache()
        return name in cls.set1 or name in cls.set2
    @classmethod
    def get_packages(cls, name):
        ret = []
        output = get_output('tasksel --task-packages '+name)
        for line in output.split('\n'):
            if line.startswith('W: '): continue # skip warning messages, such as Duplicate sources.list entry
            item = line.strip()
            if item: ret.append(item)
        return ret
    @classmethod
    def install(cls, name):
        is_string_not_empty(name)
        cls.install_tasksel_package()
        APT.install( *cls.get_packages(name) )
        cls.cache_changed()
    @classmethod
    def remove(cls, name):
        print '\x1b[1;36m', _('Inspecting safely deletable packages. Please wait for a few minutes.') ,'\x1b[m'
        import os
        path = os.path.dirname(os.path.abspath(__file__)) + '/support/safely_deletable_pkgs.py'
        command = ['python', path]
        command.extend(cls.get_packages(name))
        import subprocess
        task = subprocess.Popen(command, stdout=subprocess.PIPE)
        to_remove = []
        for line in task.stdout:
            to_remove.append(line.strip())
        task.wait()
        if to_remove:
            APT.remove( *to_remove )
            cls.cache_changed()

def window_manager_name():
    """Returns window manager name"""
    # Thanks to Whise (Helder Fraga), we have this elegant function!
    # This function is from Screenlets/sensors.py
    # GPLv3
    import gtk
    root = gtk.gdk.get_default_root_window()
    try:
        ident = root.property_get("_NET_SUPPORTING_WM_CHECK", "WINDOW")[2]
        _WM_NAME_WIN = gtk.gdk.window_foreign_new(long(ident[0]))
    except TypeError, exc:
        _WM_NAME_WIN = ""

    name = ""
    win = _WM_NAME_WIN
    if (win != None):
        try:
            name = win.property_get("_NET_WM_NAME")[2]
        except TypeError, exc:
            pass
    return name

class FedoraReposSection:
    def __init__(self, lines):
        for line in lines: assert isinstance(line, str) and line.endswith('\n')
        assert lines[0].startswith('['), lines
        
        self.name = lines[0].strip()[1:-1]
        self.lines = lines

    def is_fedora_repos(self):
        for line in self.lines:
            if line.startswith('gpgkey=') and 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch' in line:
                return True
        return False

    def part2_of(self, line):
        for word in ['/releases/', '/development/', '/updates/']:
            pos = line.find(word)
            if pos != -1:
                return line[pos:]
        else:
            raise CommandFailError('No /releases/, /development/ or /updates/ found.', self.lines)

    def comment_line(self, i):
        if not self.lines[i].startswith('#'):
            self.lines[i] = '#' + self.lines[i] 

    def uncomment_line(self, i):
        if self.lines[i].startswith('#'):
            self.lines[i] = self.lines[i][1:] 

    def change_baseurl(self, new_url):
        for i, line in enumerate(self.lines):
            if 'mirrorlist=' in line:
                self.comment_line(i)
            elif 'baseurl=' in line:
                self.uncomment_line(i)
        for i, line in enumerate(self.lines):
            if line.startswith('baseurl='):
                self.lines[i] = 'baseurl=' + new_url + self.part2_of(line)

    def write_to_stream(self, stream):
        stream.writelines(self.lines)
    
    def enabled(self):
        return 'enabled=1\n' in self.lines

class FedoraReposFile:
    def __init__(self, path):
        assert isinstance(path, str) and path.endswith('.repo')

        self.path = path

        self.sections = []
        with open(path) as f:
            contents = f.readlines()
        while contents[0].startswith('#') or contents[0].strip() == '': # skip comments and blank lines at the beginning
            del contents[0]
        lines = []
        for line in contents:
            if line.startswith('[') and lines:
                section = FedoraReposSection(lines)
                self.sections.append(section)
                lines = []
            lines.append(line)
        section = FedoraReposSection(lines)
        self.sections.append(section)

    def change_baseurl(self, new_url):
        changed = False
        for section in self.sections:
            if section.is_fedora_repos():
                section.change_baseurl(new_url)
                changed = True

        if not changed: return
        with TempOwn(self.path) as o:
            with open(self.path, 'w') as f:
                for section in self.sections:
                    section.write_to_stream(f)

    @classmethod
    def all_repo_paths(cls):
        import glob
        return glob.glob('/etc/yum.repos.d/*.repo')

    @classmethod
    def all_repo_objects(cls):
        ret = []
        for path in cls.all_repo_paths():
            obj = FedoraReposFile(path)
            ret.append(obj)
        return ret

def get_ailurus_version():
    import os
    path = os.path.dirname(os.path.abspath(__file__)) + '/version'
    with open(path) as f:
        return f.read().strip()
    
def get_ailurus_release_date():
    import os, time
    path = os.path.dirname(os.path.abspath(__file__)) + '/version'
    info = os.stat(path)
    return time.strftime('%Y-%m-%d', time.gmtime(info.st_mtime))

try:
    D = get_icons_path()
except: # raise exception in python console because __file__ is not defined
    import os
    D = os.path.expanduser('~/workspace/Ailurus/ailurus/icons/')
    assert os.path.exists(D)
    
try:
    AILURUS_VERSION = get_ailurus_version()
    AILURUS_RELEASE_DATE = get_ailurus_release_date()
except: # raise exception in python console because __file__ is not defined
    print_traceback()

Config.init()

install_locale()

GPL = _('GNU General Public License')
LGPL = _('GNU Lesser General Public License')
EPL = _('Eclipse Public License')
MPL = _('Mozilla Public License')
BSD = _('Berkeley Software Distribution License')
MIT = _('MIT License')
CDDL = _('Common Development and Distribution License')
APL = _('Aptana Public License')
AL = _('Artistic License')

import atexit
atexit.register(ResponseTime.save)
atexit.register(KillWhenExit.kill_all)
atexit.register(drop_priviledge)
try:
    firefox.init()
    atexit.register(firefox.save_user_prefs)
except: print_traceback()

try:
    import pynotify
    pynotify.init('Ailurus')
except:
    print 'Cannot init pynotify'

import random
secret_key = ''.join([chr(random.randint(97,122)) for i in range(0, 64)])

UBUNTU = Config.is_Ubuntu()
UBUNTU_DERIV = False # True value means Ubuntu derivative. For Ubuntu it is False. For Mint it is True.
MINT = Config.is_Mint()
YLMF = Config.is_YLMF()
DEEPIN = Config.is_Deepin()
FEDORA = Config.is_Fedora()
ARCHLINUX = Config.is_ArchLinux()
if UBUNTU:
    VERSION = Config.get_Ubuntu_version()
elif MINT:
    UBUNTU_DERIV = True
    VERSION = Config.get_Mint_version() # VERSION is in ['5', '6', '7', '8', '9', '10']
    VERSION = ['hardy', 'intrepid', 'jaunty', 'karmic', 'lucid', 'maverick'][int(VERSION)-5]
elif YLMF:
    UBUNTU_DERIV = True
    VERSION = Config.get_YLMF_version()
elif DEEPIN:
    UBUNTU_DERIV = True
    VERSION = Config.get_Deepin_version()
elif FEDORA:
    VERSION = Config.get_Fedora_version()
elif ARCHLINUX:
    VERSION = '' # ArchLinux has no version -_-b
else:
    print _('Your Linux distribution is not supported. :(')
    VERSION = ''

GNOME = False
KDE = False
XFCE = False
# Thank you, GShutdown Team!
# This code is from gshutdown/src/values.c
# GPLv2
WINDOW_MANAGER = window_manager_name()
if WINDOW_MANAGER == "Metacity":
    GNOME = True
elif WINDOW_MANAGER == "KWin":
    KDE = True
elif WINDOW_MANAGER == "Xfwm4":
    XFCE = True
else:
    print 'Window Manager is not recognized:', WINDOW_MANAGER
    # These functions are less effective, but they work.
    GNOME = Config.is_GNOME()
    KDE = Config.is_KDE()
    XFCE = Config.is_XFCE()
