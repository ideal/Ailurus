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

def get():
    return [
_('''Set apt source
sudo software-properties-gtk
sudo software-properties-kde'''),

_('''Display the packages which are not installed but have remained residual config
dpkg -l | awk '/^rc/ {print $2}'
'''),

_('''Add a PPA repository:
sudo add-apt-repository ppa:PPA-REPOSITORY-NAME
'''),

_("""Display a list of files. The files are installed from a given package.
dpkg -L PACKAGE_NAME
"""),

_("""Display a list of packages. The packages installed a given file.
dpkg -S FILE_NAME
"""),

_("""Display a list of packages. The name of packages matches given regex pattern.
apt-cache search REG_EXPRESSION
"""),

_("""Display a list of packages. The packages provide a given file.
apt-file search FILE_NAME
"""),

_("""Display a list of packages. The given package depends on the list of packages.
apt-cache depends PACKAGE_NAME
"""),

_("""Display a list of packages. These packages depend on the given package.
apt-cache rdepends PACKAGE_NAME
"""),

_("""Prompt for a disk to be inserted and then add the disc to the source list.
sudo apt-cdrom add
"""),

_("""Install the newest versions of all packages currently installed on the system.
sudo apt-get upgrade
"""),

_("""Delete residual package configuration files.
dpkg -l | grep ^rc | awk '{print $2}' | sudo xargs dpkg -P
"""),

_("""Automatically install necessary files for './configure ; make ; make install'
sudo auto-apt run ./configure
"""),

_("""Save the list of packages currently installed on your system.
dpkg --get-selections | grep -v deinstall > SOME_FILE
Then use the file to restore packages. 
dpkg --set-selections < SOME_FILE ; sudo dselect
"""),

_("""After running "sudo apt-get install", "*.deb" files are stored in "/var/cache/apt/archives"
You can clean this directory by:
sudo apt-get clean
"""),

_("""Display URL for a given package
apt-get -qq --print-uris install PACKAGE_NAME
"""),

_("""Display some statistics about the apt cache
apt-cache stats
"""),

_("""Display all package name
apt-cache pkgnames
"""),

_("""Display some information of a given package
apt-cache show PACKAGE_NAME

"""),

]