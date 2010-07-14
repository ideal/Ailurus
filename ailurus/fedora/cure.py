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
import sys, os
from lib import *

class Colorful_BASH_prompt_symbols(C):
    __doc__ = _('Use colorful Bash prompt symbols')
    detail = (_('Add this line into ~/.bashrc:') + '\n' +
              r"PS1='\[\033[01;32m\]\u@\h\[\033[00m\] \[\033[01;34m\]\W\[\033[00m\]\\$ '")
    bashrc = os.path.expanduser('~/.bashrc')
    line = r"PS1='\[\033[01;32m\]\u@\h\[\033[00m\] \[\033[01;34m\]\W\[\033[00m\]\\$ '"
    def exists(self):
        return not file_contain(self.bashrc, self.line)
    def cure(self):
        file_append(self.bashrc, self.line)
        notify( _('The color of bash prompt symbols is changed.'), _('It will take effect at the next time you log in.') )

class Install_Stardict_dictionary(C):
    __doc__ = _('Install Stardict dictionaries')
    def exists(self):
        if not RPM.installed('stardict'):
            return False
        self.pkgs = []
        locale1 = Config.get_locale()
        locale2 = locale1.split('_')[0]
        pkg1 = 'stardict-dic-' + locale1
        pkg2 = 'stardict-dic-' + locale2
        for p in [pkg1, pkg2]:
            if RPM.exist(p) and not RPM.installed(p):
                self.pkgs.append(p)
        self.detail = _('Command:') + ' yum install ' + ' '.join(self.pkgs)
        return bool(self.pkgs)
    def cure(self):
        RPM.install(*self.pkgs)

