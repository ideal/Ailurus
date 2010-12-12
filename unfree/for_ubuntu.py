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
# don't change sys.path
from lib import *
from libapp import *
assert UBUNTU or UBUNTU_DERIV
from ubuntu.third_party_repos import _repo

class urls:
    eset_antivirus_32 = 'http://download.eset.com/special/eav_linux/ueav.i386.linux'
    eset_antivirus_64 = 'http://download.eset.com/special/eav_linux/ueav.x86_64.linux'
    google_earch = 'http://dl.google.com/earth/client/current/GoogleEarthLinux.bin'
    google_chrome_32 = 'http://dl.google.com/linux/direct/google-chrome-stable_current_i386.deb'
    google_chrome_64 = 'http://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
    alipay = 'http://blog.alipay.com/wp-content/2008/10/aliedit.tar.gz'
    amenace = 'http://www.viewizard.com/download/amenace12.tar.bz2'
    hittex = 'http://plutothesis.googlecode.com/files/PlutoThesis_UTF8_1.9.2.20090424.zip'
    nvidia_32 = 'ftp://download.nvidia.com/XFree86/Linux-x86/195.36.24/NVIDIA-Linux-x86-195.36.24-pkg1.run'
    nvidia_64 = 'ftp://download.nvidia.com/XFree86/Linux-x86_64/195.36.24/NVIDIA-Linux-x86_64-195.36.24-pkg2.run'
    adobeair = 'http://airdownload.adobe.com/air/lin/download/latest/adobeair.deb'
    picasa_32 = 'http://dl.google.com/linux/deb/pool/non-free/p/picasa/picasa_3.0-current_i386.deb'
    picasa_64 = 'http://dl.google.com/linux/deb/pool/non-free/p/picasa/picasa_3.0-current_amd64.deb'
    truecrypt32 = 'http://www.truecrypt.org/download/truecrypt-7.0-linux-x86.tar.gz'
    truecrypt64 = 'http://www.truecrypt.org/download/truecrypt-7.0-linux-x64.tar.gz'

#class Alice(_path_lists):
#    __doc__ = _('Alice: A new way to learn programming')
#    detail = _('A storytelling application, especially appropriate for middle school students.')
#    download_url = 'http://www.alice.org/' 
#    category = 'education'
#    def __init__(self):
#        self.dir = '/opt/Alice 2.2'
#        self.shortcut = '/usr/share/applications/alice.desktop'
#        self.paths = [ self.dir, self.shortcut ]
#    def install(self):
#        if is32():
#            f = R(
#['http://tdt.sjtu.edu.cn/S/Alice2.2b_i386.tar.bz2',],
#296544228, '0c6340a5b52d72abc12c394561d61c3ccba21ca7').download()
#        else:
#            f = R(
#['http://tdt.sjtu.edu.cn/S/Alice2.2b_x86_64.tar.bz2',],
#296519582, '7558fa7f22d13f8d18671b3efc44374541c5a506').download()
#
#        import os
#        if not os.path.exists('/opt'):
#            run_as_root('mkdir /opt')
#        own_by_user('/opt')
#        with Chdir('/opt'):
#            run('tar jxf '+f)
#            assert os.path.exists(self.dir)
#            create_file(self.shortcut, '''[Desktop Entry]
#Name=Alice
#Exec=bash "/opt/Alice 2.2/Required/alice.sh"
#Path=/opt/Alice 2.2/Required/
#Encoding=UTF-8
#StartupNotify=true
#Terminal=false
#Type=Application
#Categories=Education;Science; ''')

class AliPayFirefoxPlugin(I):
    __doc__ = _('Alipay ( Zhi Fu Bao ) security plugin for Firefox')
    download_url = 'http://blog.alipay.com/301.html'
    category = 'firefox_extension'
    Chinese = True
    def __init__(self):
        import os
        self.path = os.path.expanduser('~/.mozilla/plugins')
    def install(self):
        file = '/tmp/aliedit.tar.gz'
        run('wget --timeout=60 %s -O /tmp/aliedit.tar.gz' % urls.alipay)
        path = self.path
        import os
        if not os.path.exists(path):
            run('mkdir -p %s'%path)
        with Chdir(path):
            run('tar zxf %s'%file)
    def installed(self):
        import os
        return (
          (os.path.exists(self.path+'/aliedit.so') and os.path.exists(self.path+'/aliedit.xpt'))
             or
          (os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.so')
             and os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.xpt'))
          )
    def remove(self):
        run('rm -f %s'%(self.path+'/aliedit.so') )
        run('rm -f %s'%(self.path+'/aliedit.xpt') )
        if os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.so'):
            run_as_root('rm -f /usr/lib/firefox-addons/plugins/aliedit.so')
        if os.path.exists('/usr/lib/firefox-addons/plugins/aliedit.xpt'):
            run_as_root('rm -f /usr/lib/firefox-addons/plugins/aliedit.xpt')
    def visible(self):
        import os
        return os.path.exists('/usr/bin/firefox')

class AstroMenace(_path_lists):
    'AstroMenace'
    detail = _('Drive a spaceship and battle against invaders! Collect money during the combat. Upgrade armaments and weapons.')
    download_url = 'http://www.viewizard.com/'
    category = 'game'
    def __init__(self):
        self.paths = ['/opt/astromenace', '/usr/share/applications/astromenace.desktop']
    def install(self):
        f = R(urls.amenace).download()

        import os
        if not os.path.exists('/opt'): run_as_root('mkdir /opt')
        run_as_root('chown $USER:$USER /opt')
        with Chdir('/opt'):
            run('tar xf %s'%f)
            create_file('/usr/share/applications/astromenace.desktop', 
'''[Desktop Entry]
Name=AstroMenace
Exec=/opt/astromenace/game_launcher
Path=/opt/astromenace/
Icon=/opt/astromenace/astromenace_64.png
Encoding=UTF-8
StartupNotify=true
Terminal=false
Type=Application
Categories=Game;''')

class ChineseAcademyofSciencesTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _('LaTeX Thesis Templates by Chinese Academy of Sciences')
    import os
    detail = _('After installation, a file "CASthesis.zip" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(
['http://tdt.sjtu.edu.cn/S/CASthesis-v0.1j.zip',],
244765, 'dc84597ee626b7a2dcd3ee8825d2e374f6822197')
        import os
        self.file = os.path.expanduser('~/CASthesis.zip')
     
class XJTUTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _("LaTeX Thesis Templates by Xi\'an Jiaotong University, China")
    import os
    detail = _('After installation, a file "XJTUthesis.rar" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(
['http://tdt.sjtu.edu.cn/S/XJTUthesis.rar',],
3009431, '88ce43f6396d76fff56b597a2a35487548fdaa54')
        import os
        self.file = os.path.expanduser('~/XJTUthesis.rar')

class HITTeXTemplate(_download_one_file) :
    # cannot find out which license it is released under
    __doc__ = _('LaTeX Thesis Templates by Harbin Institute of Technology, China')
    import os
    detail = _('After installation, a file "HITthesis.rar" is placed in the folder "%s".')%os.path.expanduser('~')
    category = 'latex'
    Chinese = True
    def __init__(self):
        self.R = R(urls.hittex)
        import os
        self.file = os.path.expanduser('~/HITthesis.rar')

class FFJavaScriptDebugger(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('JavaScript Debugger: a powerful JavaScript debugger')
    detail = ''
    download_url = 'https://addons.mozilla.org/en-US/firefox/addon/216'
    name = u'JavaScript Debugger'
    R = R(latest(216), filename='javascript_debugger.xpi')

class FFMacOSXTheme(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('Mac OS X Theme')
    detail = ''
    download_url = 'https://addons.mozilla.org/en-US/firefox/addon/7172'
    name = u'MacOSX Theme'
    R = R(latest(7172), filename='macosx_theme.jar')

class FFNetVideoHunter(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('NetVideoHunter: Download videoclips from video-sharing web sites')
    detail = ''
    download_url = 'https://addons.mozilla.org/en-US/firefox/addon/7447'
    name = u'NetVideoHunter'
    R = R(latest(7447), filename='netvideohunter.xpi')

class FFPersonas(_ff_extension): # cannot find out which license it is released under
    __doc__ = _('Personas: One-click changing Firefox skin')
    detail = _('Theme your browser according to your mood, hobby or season.')
    download_url = 'https://addons.mozilla.org/en-US/firefox/addon/10900'
    name = u'Personas'
    R = R(latest(10900), filename='personas.xpi')
        
class GoogleEarth(I):
    __doc__ = _('Google Earth')
    detail = _('Please install it in /opt/google-earth. Otherwise it cannot be detected.')
    category = 'others'
    def install(self):
        f = R(urls.google_earch).download()
        os.system('chmod a+x ' + f)
        run_as_root_in_terminal(f)
    def installed(self):
        return os.path.exists('/opt/google-earth')
    def remove(self):
        run_as_root_in_terminal('/opt/google-earth/uninstall')

class NVIDEA_Driver(I):
    __doc__ = 'NVIDEA ' + _('video card driver')
    category = 'others'
    if is32(): download_url = urls.nvidia_32
    else:      download_url = urls.nvidia_64
    def install(self):
        f = R(self.download_url).download()
        os.system('chmod a+x ' + f)
        run_as_root_in_terminal(f)
    def installed(self):
        return False
    def remove(self):
        raise NotImplementedError

class ATI_Driver(I):
    __doc__ = 'ATI ' + _('video card driver')
    category = 'others'
    download_url = 'http://ati.amd.com/support/driver.HTML'
    def install(self):
        open_web_page('http://ati.amd.com/support/driver.HTML')
    def installed(self):
        return False
    def remove(self):
        raise NotImplementedError

class Google_Chrome(I):
    'Google Chrome'
    download_url = 'http://www.google.com/chrome'
    category = 'browser'
    def install(self):
        if is32(): f = R(urls.google_chrome_32).download()
        else:      f = R(urls.google_chrome_64).download()
        APT.install_local(f)
    def installed(self):
        return APT.installed('google-chrome-stable')
    def remove(self):
    	if APT.installed('google-chrome-beta'):
    		APT.remove('google-chrome-beta')
        APT.remove('google-chrome-stable')

class ESETNOD32(I):
    'ESET NOD32'
    detail = _('Anti virus and anti spyware')
    download_url = 'http://beta.eset.com/linux'
    category = 'antivirus'
    def install(self):
        if is32():
            f = R(urls.eset_antivirus_32).download()
        else:
            f = R(urls.eset_antivirus_64).download()
        run('chmod +x ' + f)
        run_as_root(f)
        if not is32():
            # Fix bug because /usr/lib/libesets_pac.so cannot run on x86_64
            with TempOwn('/etc/ld.so.preload'):
                with open('/etc/ld.so.preload') as f:
                    content = f.read()
                with open('/etc/ld.so.preload', 'w') as f:
                    for item in content.split():
                        if 'libesets_pac.so' not in item:
                            print >>f, item, 
    def installed(self):
        return os.path.exists('/opt/eset/esets/bin/esets_gil')
    def remove(self):
        run_as_root('/opt/eset/esets/bin/esets_gil')

class Repo_Oracle(_repo):
    __doc__ = _('Oracle')
    def __init__(self):
        self.detail = _('This repository provides Oracle Database Express Edition.\n'
            'After installing Oracle Database, please add yourself to the "dba" group, then run "sudo /etc/init.d/oracle-xe configure".')
        self.apt_content = 'oracle-xe oracle-xe-client oracle-xe-universal'
        self.web_page = 'http://oss.oracle.com/'
        self.apt_file = '/etc/apt/sources.list.d/oracle.list'
        self.apt_conf = [ 'deb http://oss.oracle.com/debian unstable main non-free' ]
        self.key_url = 'http://oss.oracle.com/el4/RPM-GPG-KEY-oracle'
        self.key_id = 'B38A8516'
        _repo.__init__(self)

class AdobeAIR(I):
    'Adobe AIR'
    detail = _('Use HTML, JavaScript and Flash to build desktop applications')
    download_url = 'http://get.adobe.com/air/'
    category = 'ide'
    def install(self):
        f = R(urls.adobeair).download()
        APT.install_local(f)
    def installed(self):
        return APT.installed('adobeair')
    def remove(self):
        APT.remove('adobeair')

class Picasa(I):
    'Picasa'
    detail = _('An image organizer and image viewer, plus photo-sharing function')
    if is32():
        download_url = urls.picasa_32
    else:
        download_url = urls.picasa_64
    category = 'image'
    def install(self):
        f = R(self.download_url).download()
        APT.install_local(f)
    def installed(self):
        return APT.installed('picasa')
    def remove(self):
        APT.remove('picasa')

class Mendeley(_apt_install):
    'Mendeley'
    detail = _('Organizes research paper collection and citations. It automatically generates bibliographies.')
    pkgs = 'mendeleydesktop'
    category = 'latex'
    deb = None
    i = ord(VERSION[0]) - ord('h') # 8.04=0, 8.10=1
    a = 8 + i / 2
    if i%2 == 0: b = '04'
    else: b = '10'
    deb = 'deb http://www.mendeley.com/repositories/xUbuntu_%s.%s /' % (a, b)

class TrueCrypt(I):
    __doc__ = _('TrueCrypt: Open-Source disk encryption software')
    detail = _('Create a virtual encrypted disk or encrypt an entire partition')
    category = 'security'
    def installed(self):
        return os.path.exists('/usr/bin/truecrypt')
    def remove(self):
        run_as_root('/usr/bin/truecrypt-uninstall.sh')
    def install(self):
        if is32():
            url = urls.truecrypt32
            pattern = 'truecrypt-*-setup-x86'
        else:
            url = urls.truecrypt64
            pattern = 'truecrypt-*-setup-x64'
        f = R(url).download()
        with Chdir('/tmp'):
            run('tar xf "%s"' % f)
            import glob
            path = glob.glob(pattern)[0]
            path = os.path.abspath(path)
            run_as_root(path)
