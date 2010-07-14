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

'''may output repeat results'''

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/../') # Without this line, error happens. I don't know the reason. *Sigh*
from lib import *
import platform, glob, sqlite3

fedora_version = platform.dist()[1] # "12" or "13"

if is32(): fedora_arch = 'i386'
else: fedora_arch = 'x86_64'

all_enabled_sections = []
repo_objs = FedoraReposFile.all_repo_objects()
for repo in repo_objs:
    for section in repo.sections:
        assert isinstance(section, FedoraReposSection)
        if section.enabled():
            all_enabled_sections.append(section.name)

all_dirs = [ '/var/cache/yum/%s/%s/%s/' % (fedora_arch, fedora_version, section_name)
             for section_name in all_enabled_sections ]

all_databases = []
for dir in all_dirs:
    all_databases += glob.glob(dir+'*primary.sqlite') # not good. To read filename from repomd.xml is better.

all_package_names = []
for database in all_databases:
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('select name from packages')
    while True:
        row = cur.fetchone()
        if not row: break
        package_name = row[0]
        print package_name
    con.close()