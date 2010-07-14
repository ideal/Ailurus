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
import dbus
import dbus.service
import dbus.glib
import gobject
import os
import subprocess
import ctypes
import gc
try:
    import apt, apt_pkg, apt.debfile
except ImportError: # This is not Debian or Ubuntu
    pass
else:
    apt_pkg.init()

version = 10 # must be integer

class AccessDeniedError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.AccessDeniedError'

class CommandFailError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.CommandFailError'

class CannotLockAptCacheError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.CannotLockAptCacheError'

class AptPackageNotExistError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.AptPackageNotExistError'

class LocalDebPackageResolutionError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.LocalDebPackageResolutionError'

class CannotUpdateAptCacheError(dbus.DBusException):
    _dbus_error_name = 'cn.ailurus.CannotUpdateAptCacheError'

class AilurusFulgens(dbus.service.Object):
    @dbus.service.method('cn.ailurus.Interface', 
                                          in_signature='ss', 
                                          out_signature='', 
                                          sender_keyword='sender')
    def run(self, command, env_string, sender=None):
        self.check_permission(sender)
        command = command.encode('utf8')
        env_string = env_string.encode('utf8')
        env = self.__get_dict(env_string)
        os.chdir(env['PWD'])
        task = subprocess.Popen(command, shell=True, env=env)
        task.wait()
        if task.returncode:
            raise CommandFailError(command, task.returncode)

    @dbus.service.method('cn.ailurus.Interface', 
                                          in_signature='ss', 
                                          out_signature='i', 
                                          sender_keyword='sender')
    def spawn(self, command, env_string, sender=None):
        self.check_permission(sender)
        command = command.encode('utf8')
        env_string = env_string.encode('utf8')
        env = self.__get_dict(env_string)
        os.chdir(env['PWD'])
        task = subprocess.Popen(command, shell=True, env=env)
        return task.pid

    @dbus.service.method('cn.ailurus.Interface', 
                                          in_signature='', 
                                          out_signature='i') 
    def get_check_permission_method(self):
        return self.check_permission_method

    @dbus.service.method('cn.ailurus.Interface', 
                                          in_signature='', 
                                          out_signature='i') 
    def get_version(self):
        return version

    @dbus.service.method('cn.ailurus.Interface', 
                                          in_signature='', 
                                          out_signature='',
                                          sender_keyword='sender')
    def exit(self, sender=None):
        self.check_permission(sender)
        self.mainloop.quit()

    def check_permission(self, sender):
        if sender in self.authorized_sender:
            return
        else:
            if self.check_permission_method == 0:
                self.__check_permission_0(sender)
            elif self.check_permission_method == 1:
                self.__check_permission_1(sender)
            else:
                raise Exception
            self.authorized_sender.add(sender)

    def __init__(self, mainloop):
        self.mainloop = mainloop # use to terminate mainloop
        self.authorized_sender = set()
        bus_name = dbus.service.BusName('cn.ailurus', bus = dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, '/')
        self.apt_cache = None # an instance of apt.cache.Cache
        self.lock1_fd = -1 # a fd
        self.lock2_fd = -1 # a fd
        self.holding_apt_lock = False
    
        self.check_permission_method = -1
        try:
            obj = dbus.SystemBus().get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
            obj = dbus.Interface(obj, 'org.freedesktop.PolicyKit1.Authority')
            self.check_permission_method = 1
        except dbus.DBusException:
            obj = dbus.SystemBus().get_object('org.freedesktop.PolicyKit', '/')
            obj = dbus.Interface(obj, 'org.freedesktop.PolicyKit')
            self.check_permission_method = 0
        if self.check_permission_method == -1: raise Exception

    def __check_permission_0(self, sender):
        if not sender: raise ValueError('sender == None')
        
        obj = dbus.SystemBus().get_object('org.freedesktop.PolicyKit', '/')
        obj = dbus.Interface(obj, 'org.freedesktop.PolicyKit')
        granted = obj.IsSystemBusNameAuthorized('cn.ailurus', sender, False)
        if 'yes' != granted:
            raise AccessDeniedError('Session is not authorized. Authorization method = 0')

    def __check_permission_1(self, sender):
        # This function is from project "gnome-lirc-properties". Thanks !
        if not sender: raise ValueError('sender == None')
        
        obj = dbus.SystemBus().get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
        obj = dbus.Interface(obj, 'org.freedesktop.PolicyKit1.Authority')
        (granted, _, details) = obj.CheckAuthorization(
                ('system-bus-name', {'name': sender}), 'cn.ailurus', {}, dbus.UInt32(1), '', timeout=600)
        if not granted:
            raise AccessDeniedError('Session is not authorized. Authorization method = 1')

    def __get_dict(self, string):
        assert string.endswith('\n')
        List = string.split('\n')
        Dict = {}
        for i in range(0, len(List)-1, 2):
            k = List[i]
            v = List[i+1]
            Dict[k] = v
        return Dict
    
    @dbus.service.method('cn.ailurus.Interface',
                                    in_signature='',
                                    out_signature='',
                                    sender_keyword='sender')
    def drop_priviledge(self, sender=None):
        if sender in self.authorized_sender:
            self.authorized_sender.remove(sender)

    def __prepare_env(self, env_string):
        env_dict = self.__get_dict(env_string)
        if 'TERM' not in env_dict: env_dict['TERM'] = 'xterm'
        env_dict['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        for key in ['DISPLAY', 'TERM', 'PATH']:
            os.putenv(key, env_dict[key])

    @dbus.service.method('cn.ailurus.Interface', in_signature='sss', out_signature='', sender_keyword='sender')
    def apt_command(self, command, argument, env_string, sender=None):
        self.check_permission(sender)
        self.__prepare_env(env_string)
        self.apt_window, self.apt_progress = self.create_apt_window()
        try:
            self.apt_lock_cache()
            self.apt_open_cache()
            if command == 'install':
                self.apt_install(argument)
            elif command == 'install_local':
                self.apt_install_local(argument)
            elif command == 'remove':
                self.apt_remove(argument)
            elif command == 'update':
                self.apt_update()
            else:
                raise Exception('unknown command', command)
        finally:
            self.apt_unlock_cache()
            self.apt_window.destroy()
            self.apt_window = self.apt_progress = None
    
    def lock_apt(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        lockfile = path + 'lock'
        # This will create an empty file of the given name and lock it. 
        # Once this is done all other calls to GetLock in any other process will fail with -1. 
        # The return result is the fd of the file, the call should call close at some time
        lock = apt_pkg.GetLock(lockfile)
        if lock < 0:
            raise CannotLockAptCacheError(lockfile)
        return lock
    
    def apt_lock_cache(self):
        # /var/lib/apt/lists/lock, 
        # locked by apt-get update
        self.lock1_fd = self.lock_apt(apt_pkg.Config.FindDir("Dir::State::Lists"))
        # /var/cache/apt/archives/lock,
        # try the lock in /var/cache/apt/archive/lock first
        # this is because apt-get install will hold it all the time
        # while the dpkg lock is briefly given up before dpkg is
        # forked off. this can cause a race (LP: #437709)
        self.lock2_fd = self.lock_apt(apt_pkg.Config.FindDir("Dir::Cache::Archives"))
        try:
            apt_pkg.PkgSystemLock()
        except SystemError:
            raise CannotLockAptCacheError('apt_pkg.PkgSystemLock')
        self.holding_apt_lock = True
    
    @dbus.service.method('cn.ailurus.Interface', in_signature='', out_signature='b')
    def is_apt_cache_lockable(self):
        if self.holding_apt_lock:
            return True
        try:
            self.apt_lock_cache()
            return True
        finally:
            self.apt_unlock_cache()

    def close_lock1(self):
        if self.lock1_fd > 0:
            os.close(self.lock1_fd)
            self.lock1_fd = -1

    def close_lock2(self):
        if self.lock2_fd > 0:
            os.close(self.lock2_fd)
            self.lock2_fd = -1
    
    def unlock_apt_pkg_global_lock(self):
        try: apt_pkg.PkgSystemUnLock()
        except SystemError: pass # E:Not locked
    
    def apt_unlock_cache(self):
        self.close_lock1()
        self.close_lock2()
        self.unlock_apt_pkg_global_lock()
        self.holding_apt_lock = False
    
    @dbus.service.method('cn.ailurus.Interface', in_signature='', out_signature='')
    def apt_open_cache(self):
        if self.apt_cache: self.apt_cache.open()
        else: self.apt_cache = apt.cache.Cache()

    @dbus.service.method('cn.ailurus.Interface', in_signature='', out_signature='')
    def apt_close_cache(self):
        self.apt_cache = None
        gc.collect()

    @dbus.service.method('cn.ailurus.Interface', in_signature='s', out_signature='b')
    def apt_package_exists(self, package_name):
        assert self.apt_cache is not None
        return package_name in self.apt_cache
    
    @dbus.service.method('cn.ailurus.Interface', in_signature='s', out_signature='b')
    def apt_package_installed(self, package_name):
        assert self.apt_cache is not None
        if package_name not in self.apt_cache: return False
        return self.apt_cache[package_name].isInstalled

    def apt_install(self, package_names):
        '''package_names -- package names concatenated by comma (,)
        may raise apt.cache.FetchFailedException, apt.cache.FetchCancelledException, SystemError'''
        for pkg_name in package_names.split(','):
            if self.apt_cache.has_key(pkg_name):
                pkg = self.apt_cache[pkg_name]
            else:
                raise AptPackageNotExistError(pkg_name)
            pkg.mark_install()
        self.unlock_apt_pkg_global_lock()
        self.apt_cache.commit(self.apt_progress.fetch, self.apt_progress.install)
        apt_pkg.PkgSystemLock()

    def apt_remove(self, package_names):
        '''package_names -- package names concatenated by comma (,)'''
        for pkg_name in package_names.split(','):
            if self.apt_cache.has_key(pkg_name):
                pkg = self.apt_cache[pkg_name]
            else:
                raise AptPackageNotExistError(pkg_name)
            pkg.mark_delete()
        self.unlock_apt_pkg_global_lock()
        self.apt_cache.commit(self.apt_progress.fetch, self.apt_progress.install)
        apt_pkg.PkgSystemLock()

    def apt_install_local(self, package_path):
        deb = apt.debfile.DebPackage(package_path, self.apt_cache)
        if not deb.check(): raise LocalDebPackageResolutionError
        self.unlock_apt_pkg_global_lock()
        (install, remove, unauth) = deb.required_changes
        for name in install:
            self.apt_cache[name].mark_install()
        for name in remove:
            self.apt_cache[name].mark_delete()
        self.apt_cache.commit(self.apt_progress.fetch, self.apt_progress.install)
        deb.install(self.apt_progress.dpkg_install)
        apt_pkg.PkgSystemLock()

    def apt_update(self):
        try:
            self.apt_cache.update(self.apt_progress.fetch)
        except SystemError, e: raise CannotUpdateAptCacheError(e.message)

    def create_apt_window(self):
        import gtk
        import apt.progress.gtk2
        window = gtk.Window()
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_deletable(False)
        window.set_resizable(False)
        progress = apt.progress.gtk2.GtkAptProgress()
        progress.set_size_request(700, -1)
        window.add(progress)
        window.iconify()
        window.show_all()
        return window, progress

def main(): # revoked by ailurus-daemon
    try:
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(15, 'ailurus-daemon', 0, 0, 0) # change_task_name
    except: pass
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    mainloop = gobject.MainLoop()
    AilurusFulgens(mainloop)
    mainloop.run()

if __name__ == '__main__':
    main()