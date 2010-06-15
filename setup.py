#!/usr/bin/env python
import os, sys
from distutils.core import setup
try:
    from DistUtilsExtra.command import *
except ImportError:
    print 'Cannot install Ailurus :('
    print 'Would you please install package "python-distutils-extra" first?'
    sys.exit()
from glob import glob

f = open('ailurus/version')
version = f.read().strip()
f.close()

setup(name = 'ailurus',
      description = 'makes Linux easier to use',
      long_description = 
'''Ailurus is an application which makes Linux easier to use.

Features:
* Help users learn some Linux skills
* Install/remove some nice applications
* Enable/disable some third party repositories
* Display information about BIOS, motherboard, CPU and battery
* Show/Hide Computer, Home folder, Trash icon and Network icon on desktop
* Configure Nautilus thumbnail cache
* Configure Nautilus context menu
* Configure Window behavior
* Configure GNOME auto-start applications
* Show/Hide GNOME splash screen
''',
      version = version,
      maintainer = 'Homer Xing',
      maintainer_email = 'homer.xing@gmail.com',
      url = 'http://ailurus.googlecode.com/',
      license = 'GPLv2+',
      platforms = ['linux'],
      packages = ['ailurus', 'ailurus.common', 'ailurus.gnome', 'ailurus.archlinux', 'ailurus.fedora', 'ailurus.ubuntu', 'ailurus.support', ],
      package_data={'ailurus': ['native_apps', 'version', 
                                'icons/appicons/*', 'icons/sora_icons/*', 'icons/suyun_icons/*', 'icons/umut_icons/*', 'icons/velly_icons/*', ],
                    'ailurus.support': ['MTJ_urls', 'fedora_server_list', 'ubuntu_server_list']},
      data_files = [
        ('share/man/man1/', ['ailurus.1']),
        ('share/applications/', ['ailurus.desktop']),
        
        ('share/ailurus/', ['ChangeLog']),
        ('share/dbus-1/system-services/', ['support/dbus/cn.ailurus.service']),
        ('/etc/dbus-1/system.d/', ['support/dbus/cn.ailurus.conf']),
        ('share/PolicyKit/policy/', ['support/policykit0/cn.ailurus.policy']),
        ('share/polkit-1/actions/', ['support/policykit1/cn.ailurus.policy']),
        ('share/ailurus/support/', [ e for e in glob('support/*') if os.path.isfile(e)] ),
        ('share/ailurus/support/', ['support/dbus/cn.ailurus.service', 'support/dbus/cn.ailurus.conf']),
      ],
      scripts = ['bin/ailurus'],
      cmdclass = { 'build' :  build_extra.build_extra,
                   'build_i18n' :  build_i18n.build_i18n,
                   'build_help' :  build_help.build_help,
                   'build_icons' :  build_icons.build_icons
                 }
      )
