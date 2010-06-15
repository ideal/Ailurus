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

common = __import__('common')
if GNOME: import gnome as desktop
else: desktop = None
if UBUNTU_DERIV or UBUNTU: import ubuntu as distribution
elif FEDORA: import fedora as distribution
elif ARCHLINUX: import archlinux as distribution
else: distribution = None

def check_class_members(app_class):
    import types
    if type(app_class)!=types.ClassType: raise TypeError, app_class
    if not hasattr(app_class,'category'): app_class.category = 'others'
    if type( getattr(app_class,'category','') ) != str: raise TypeError, app_class
    if not hasattr(app_class, 'detail'): app_class.detail=''
    if type( getattr(app_class,'detail','') ) != str: app_class.detail = str( getattr(app_class,'detail','') ) 
    if app_class.__doc__ is None: app_class.__doc__ = app_class.__name__
    return app_class

def load_app_icon(name):
    import os
    for dir in ['other_icons/', 'appicons/']:
        path = D + dir + name + '.png'
        if os.path.exists(path): break
    else:
        path = D + 'sora_icons/default_application_icon.png'
    import gtk
    return gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)

def load_app_from_file():
    objs = []
    import ConfigParser
    from libapp import N
    import lib
    import strings
    import os
    import new
    c = ConfigParser.RawConfigParser()
    c.optionxform = str # case sensitive in option_name
    try:
        c.read(os.path.dirname(__file__) + '/native_apps')
    except:
        print_traceback()
        return []
    
    for secs in c.sections():
        try:
            is_string_not_empty(secs)
            dict = {}       
            for ops in c.options(secs):
                value = c.get(secs, ops)
                if ops == 'ubuntu' and (UBUNTU or UBUNTU_DERIV):
                    dict['pkgs'] = value
                elif ops == 'fedora' and FEDORA:
                    dict['pkgs'] = value
                elif ops == 'archlinux' and ARCHLINUX:
                    dict['pkgs'] = value
                elif ops == 'Chinese':
                    dict[ops] = True
                elif ops == 'Poland':
                    dict[ops] = True
                elif ops == 'license':
                    ls = value.split()
                    ls = [getattr(lib, e) for e in ls]
                    if len(ls)==1: dict[ops] = ls[0]
                    elif len(ls)==2: dict[ops] = DUAL_LICENSE(ls[0],ls[1])
                    elif len(ls)==3: dict[ops] = TRI_LICENSE(ls[0],ls[1],ls[2])
                else:
                    dict[ops] = value
            
            assert hasattr(strings, secs+'_0'), secs
            assert hasattr(strings, secs+'_1'), secs
            dict['__doc__'] = getattr(strings, secs + '_0')
            if dict['__doc__'] == 'FIXME' : dict['__doc__'] =''
            dict['detail'] = getattr(strings, secs + '_1')
            if dict['detail'] == 'FIXME' : dict['detail'] = ''
            if dict.has_key('pkgs') and dict['pkgs'] == 'FIXME' : continue # means not supported in this version
            if dict.has_key('Chinese') and Config.is_Chinese_locale()==False: continue # means such software provides Chinese locale only
            if dict.has_key('Poland') and Config.is_Poland_locale()==False: continue # means such software provides Poland locale only

            obj = new.classobj(secs, (N,), {})()
            for key in dict.keys():
                setattr(obj,key,dict[key])
                
            if not hasattr(obj, 'category'): obj.category = 'others'
            if hasattr(obj, 'visible') and not obj.visible():continue
            obj.self_check()
            obj.fill()
                
            obj.cache_installed = obj.installed()
            if not isinstance(obj.cache_installed, bool):
                raise ValueError, 'Return type of installed() is not bool.'
            obj.showed_in_toggle = obj.cache_installed
            obj.logo_pixbuf = load_app_icon(secs)
            objs.append(obj)
        except:
            print_traceback()
    
    return objs

def load_app_objs():
    modules = []
    for module in [common, desktop, distribution]:
        import types
        assert module==None or isinstance(module, types.ModuleType)
        if module and hasattr(module, 'apps'):
            modules.append(module.apps)

    objs = []
    names = set()
    for module in modules:
        for name in dir(module):
            if name in names: continue
            if name[0]=='_' or name=='I' or name=='N': continue
            app_class = getattr(module,name)
            if not isinstance(app_class, types.ClassType) or not issubclass(app_class, I): continue
    
            try:
                check_class_members(app_class)
                app_class_obj = app_class()
                app_class_obj.self_check()
                if hasattr(app_class_obj, 'visible') and app_class_obj.visible()==False: continue
                if hasattr(app_class_obj, 'Chinese') and Config.is_Chinese_locale()==False: continue
                if hasattr(app_class_obj, 'Poland') and Config.is_Poland_locale()==False: continue
                app_class_obj.fill()
                app_class_obj.cache_installed = app_class_obj.installed()
                if not isinstance(app_class_obj.cache_installed, bool):
                    raise ValueError, 'Return type of installed() is not bool.'
                app_class_obj.showed_in_toggle = app_class_obj.cache_installed
                app_class_obj.logo_pixbuf = load_app_icon(name)
                objs.append(app_class_obj)
                names.add(name)
            except:
                print 'Cannot load class %s' % name
                print_traceback()

    return objs + load_custom_app_objs() + load_app_from_file()

def load_app_objs_from_extension(extension):
    import types
    classobjs = []
    names = set()
    for name in dir(extension):
        if name[0]=='_' or name=='I' or name=='N': continue
        if name in names: continue
        app_class = getattr(extension,name)
        if not isinstance(app_class, types.ClassType) or not hasattr(app_class, 'this_is_an_installer'): continue
        try:
            check_class_members(app_class)
            app_class_obj = app_class()
            app_class_obj.self_check()
            if hasattr(app_class_obj, 'visible') and app_class_obj.visible()==False: continue
            if hasattr(app_class_obj, 'international') and Config.is_Chinese_locale(): continue
            if hasattr(app_class_obj, 'Chinese') and Config.is_Chinese_locale()==False: continue
            app_class_obj.cache_installed = app_class_obj.installed()
            if not isinstance(app_class_obj.cache_installed, bool):
                raise ValueError, 'Return type of installed() is not bool.'
            app_class_obj.logo_pixbuf = load_app_icon(name)
            app_class_obj.showed_in_toggle = app_class_obj.cache_installed
            names.add(name)
        except:
            print 'Cannot load class %s' % name
            print_traceback()
        else:
            classobjs.append(app_class_obj)

    return classobjs

def load_custom_app_objs():
    import os
    # check whether the extension directory exist
    for path in [os.path.dirname(__file__) + '/../unfree/',
                 Config.get_config_dir()]:
        if os.path.exists(path): 
            extension_path = path
            break
    else:
        return []
    # add the extension directory to sys.path
    import sys
    sys.path.insert(0, extension_path)
    # try to load extensions
    return_value = []
    import glob
    pys = glob.glob(extension_path+'/*.py')
    for py in pys:
        filename = os.path.split(py)[1]
        basename = os.path.splitext(filename)[0]
        try:
            module = __import__(basename)
            return_value.extend( load_app_objs_from_extension(module) )
            print 'Load extension', os.path.abspath(py)
        except:
            print 'Cannot load extension', os.path.abspath(py)
    # remove the extension directory from sys.path
    sys.path.pop(0)
    return return_value

def load_R_objs():
    paths = []
    import types
    import os, glob, re
    for module in [common, desktop, distribution]:
        if module:
            assert isinstance(module, types.ModuleType)
            path = module.__name__
            assert os.path.exists(path)
            paths.append(path)
    
    files = []
    for path in paths:
        files += glob.glob(path+'/app*.py')
    
    objs = []
    for file in files:
        f = open(file)
        content = f.read()
        R_strs = re.findall(r'R\([^)]*\)', content)
        for s in R_strs:
            if '#' in s: continue #skip comment
            objs.append( eval(s) )
    
    return objs

def load_info():
    import types
    hardware_info = []
    os_info = []
    for module in [common, desktop, distribution]:
        if module:
            assert isinstance(module, types.ModuleType)
            if hasattr(module, 'hardwareinfo') and hasattr(module.hardwareinfo, 'get'):
                hardware_info.extend(module.hardwareinfo.get())
            if hasattr(module, 'osinfo') and hasattr(module.osinfo, 'get'):
                os_info.extend(module.osinfo.get())
    return hardware_info, os_info
    
def load_setting():
    import types
    ret = []
    for module in [distribution, desktop, common]:
        if module:
            assert isinstance(module, types.ModuleType)
            if hasattr(module, 'setting') and hasattr(module.setting, 'get'):
                ret.extend(module.setting.get())
    return ret

def load_study_linux_menuitems():
    import types
    for module in [common, desktop, distribution]:
        assert isinstance(module, types.ModuleType) or module == None
    
    ret = []
    for module in [common, desktop, distribution]:
        if module and hasattr(module, 'menu') and hasattr(module.menu, 'get_study_linux_menu'):
            ret.extend(module.menu.get_study_linux_menu())
    return ret

def load_preferences_menuitems():
    import types
    for module in [common, desktop, distribution]:
        assert isinstance(module, types.ModuleType) or module == None
    
    ret = []
    for module in [common, desktop, distribution]:
        if module and hasattr(module, 'menu') and hasattr(module.menu, 'get_preferences_menu'):
            ret.extend(module.menu.get_preferences_menu())
    return ret

def load_others_menuitems():
    import types
    ret = []
    for module in [common, desktop, distribution]:
        assert isinstance(module, types.ModuleType) or module == None
        if module and hasattr(module, 'menu') and hasattr(module.menu, 'get_others_menu'):
            ret.extend(module.menu.get_others_menu())
    return ret

def load_tips():
    import types
    ret = []
    for module in [common, desktop, distribution]:
        if module:
            assert isinstance(module, types.ModuleType)
            if hasattr(module, 'tips') and hasattr(module.tips, 'get'):
                ret.extend(module.tips.get())
    return ret

def load_cure_objs():
    modules = []
    for module in [common, desktop, distribution]:
        import types
        assert module==None or isinstance(module, types.ModuleType)
        if module and hasattr(module, 'cure'):
            modules.append(module.cure)
    
    objs = []
    names = set()
    for module in modules:
        for name in dir(module):
            if name in names or name == 'C': continue
            cure_class = getattr(module,name)
            if not isinstance(cure_class, types.ClassType) or not issubclass(cure_class, C): continue
            try:
                objs.append(cure_class())
            except:
                print 'Cannot load class %s' % name
                print_traceback()
    
    return objs

if __name__ == '__main__':
    APT.get_existing_pkgs_set()
    
    import time
    begin = time.time()
    load_app_objs()
    print time.time() - begin
    
    begin = time.time()
    load_custom_app_objs()
    print time.time() - begin
    
    begin = time.time()
    load_app_from_file()
    print time.time() - begin