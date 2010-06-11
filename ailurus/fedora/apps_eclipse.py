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
import sys, os
from lib import *
from libapp import *

class Eclipse(_rpm_install):
    __doc__ = _('Eclipse (basic development environment)')
    detail = _('You can install Language pack according to the instructions on the page http://www.eclipse.org/babel/downloads.php')
    category = 'ide'
    license = EPL + ' http://www.eclipse.org/org/documents/epl-v10.php'
    pkgs = 'eclipse-platform' # Eclipse without any plugin

def make_sure_installed():
    if not RPM.installed('eclipse-platform'): RPM.install('eclipse-platform')

class CDT(_rpm_install):
    __doc__ = _('CDT: C/C++ development')
    category = 'eclipse_extension'
    license = EPL + ' http://www.eclipse.org/legal/'
    pkgs = 'eclipse-cdt'

class Pydev(_rpm_install):
    __doc__ = _('Pydev: Python development')
    category = 'eclipse_extension'
    license = EPL + ' http://pydev.org/about.html'
    pkgs = 'eclipse-pydev'

class Aptana(I):
    __doc__ = _('Aptana: Web application development')
    detail = _('Due to limitation of the authors\' programming ability, Aptana cannot be removed by Ailurus.\n'
               'In order to remove Aptana, please launch Eclipse, and go to "Help" -> "About Eclipse SDK" -> "Installation Details"')
    download_url = 'http://www.aptana.org/studio/plugin'
    how_to_install = 'http://download.aptana.org/tools/studio/plugin/install/studio'
    category = 'eclipse_extension'
    license = DUAL_LICENSE(APL, GPL)
    def installed(self):
        import glob
        List = glob.glob('/usr/lib/eclipse/plugins/com.aptana.ide.*')
        return bool(List)
    def install(self):
        make_sure_installed()
        import StringIO
        msg = StringIO.StringIO()
        print >>msg, _('Please launch Eclipse, and go to "Help" -> "Install New Software".')
        print >>msg
        print >>msg, _('Click the "Add" button. Then type <b>%s</b> in "Location".')%'http://download.aptana.org/tools/studio/plugin/install/studio'
        print >>msg
        print >>msg, _('Then click the "Next" button and agree the license.')
        install_eclipse_extension_message( _('Installing Aptana'), msg )
    def remove(self):
        remove_eclipse_extesion_message(self.__class__.__name__)

class RadRails(I):
    __doc__ = _('RadRails: Ruby development')
    detail = _('Over the past RadRails was called "RDT".')
    how_to_install = 'http://download.aptana.com/tools/radrails/plugin/install/radrails-bundle'
    category = 'eclipse_extension'
    license = DUAL_LICENSE(APL, GPL)
    def installed(self):
        import glob
        List = glob.glob('/usr/lib/eclipse/plugins/com.aptana.radrails.*')
        return bool(List)
    def install(self):
        make_sure_installed()
        import StringIO
        msg = StringIO.StringIO()
        print >>msg, _('Please launch Eclipse, and go to "Help" -> "Install New Software".')
        print >>msg
        print >>msg, _('Click the "Add" button. Then type <b>%s</b> in "Location".')%'http://download.aptana.com/tools/radrails/plugin/install/radrails-bundle'
        print >>msg
        print >>msg, _('Then click the "Next" button and agree the license.')
        install_eclipse_extension_message( _('Installing RadRails\n'), msg )
    def remove(self):
        remove_eclipse_extesion_message(self.__class__.__name__)

class PDT(I):
    __doc__ = _('PDT: PHP development')
    download_url = 'http://www.eclipse.org/pdt/downloads/'
    category = 'eclipse_extension'
    license = EPL + ' http://www.eclipse.org/legal/'
    def installed(self):
        import glob
        List = glob.glob('/usr/lib/eclipse/plugins/org.eclipse.php.*')
        return bool(List)
    def install(self):
        if not RPM.installed('eclipse-dltk-sdk'):
            RPM.install('eclipse-dltk-sdk')
        import StringIO
        msg = StringIO.StringIO()
        print >>msg, _('Please launch Eclipse, and go to "Help" -> "Install New Software".')
        print >>msg
        print >>msg, _('Click the "Add" button. Then type <b>%s</b> in "Location".')%'http://www.eclipse.org/pdt/downloads/'
        print >>msg
        print >>msg, _('Then click the "Next" button and agree the license.')
        install_eclipse_extension_message( _('Installing PDT\n'), msg )
    def remove(self):
        remove_eclipse_extesion_message(self.__class__.__name__)

class PHPEclipse(_rpm_install):
    __doc__ = _('PHPEclipse: PHP development')
    category = 'eclipse_extension'
    pkgs = 'eclipse-phpeclipse'

class Subversive(I):
    __doc__ = _('Subversive: Use SVN in Eclipse')
    how_to_install = 'http://download.eclipse.org/technology/subversive/0.7/update-site/'
    category = 'eclipse_extension'
    license = EPL
    def installed(self):
        import glob
        List = glob.glob('/usr/lib/eclipse/plugins/org.eclipse.team.svn.*')
        return bool(List)
    def install(self):
        make_sure_installed()
        import StringIO
        msg = StringIO.StringIO()
        print >>msg, _('Please launch Eclipse, and go to "Help" -> "Install New Software".')
        print >>msg
        print >>msg, _('Click the "Add" button. Then type <b>%s</b> in "Location".')%'http://download.eclipse.org/technology/subversive/0.7/update-site/'
        print >>msg
        print >>msg, _('Then click the "Next" button and agree the license.')
        install_eclipse_extension_message( _('Installing Subversive\n'), msg )
    def remove(self):
        remove_eclipse_extesion_message(self.__class__.__name__)

class Subclipse(_rpm_install):
    __doc__ = _('Subclipse: Use SVN in Eclipse')
    category = 'eclipse_extension'
    pkgs = 'eclipse-subclipse'
    
class VEditor(_rpm_install):
    __doc__ = _('VEditor: Verilog and VHDL editor')
    category = 'eclipse_extension'
    pkgs = 'eclipse-veditor'

class Mylyn(_rpm_install):
    __doc__ = _('Mylyn: Task-focused UI for Eclipse')
    cagetory = 'eclipse_extension'
    pkgs = 'eclipse-mylyn'

class Photran(_rpm_install):
    __doc__ = _('Photran: Fortran development')
    cagetory = 'eclipse_extension'
    pkgs = 'eclipse-photran'

class Texlipse(_rpm_install):
    __doc__ = _('Texlipse: Edit LaTeX in Eclipse')
    cagetory = 'eclipse_extension'
    pkgs = 'eclipse-texlipse'

class MTJ(_path_lists):
    __doc__ = _('MTJ: J2ME development')
    download_url = 'http://download.eclipse.org/dsdp/mtj/downloads/drops/R-1.0.1-200909181641/'
    category = 'eclipse_extension'
    license = DUAL_LICENSE(EPL, GPL)
    def __init__(self):
        self.path = '/usr/lib/eclipse/dropins/MTJ/'
        self.paths = [ self.path ]
    def install(self):
        make_sure_installed()
        path = os.path.dirname(os.path.abspath(__file__))+'/../support/MTJ_urls'
        with open(path) as f:
            urls = f.readlines()
        urls = [u.strip() for u in urls]
        f = R(urls).download()
        run_as_root('mkdir -p '+self.path)
        run_as_root("unzip -qo %s -d %s"%(f, self.path))
