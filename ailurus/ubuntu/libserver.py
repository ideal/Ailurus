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

def _g1():
    ret = []
    path = A+'/support/ubuntu_server_list'
    with open(path) as f:
        contents = [l.strip() for l in f]
    for i in range(0, len(contents), 4):
        org = contents[i]
        country = contents[i+1] # FIXME: How to do translation?
        url = contents[i+2]
        server = contents[i+3] # FIXME: I think we do not need this field.
        ret.append([org, country, url, server])
    return ret

def _g2(): # I have submitted these servers to archivemirrors on launchpad
    return [ 
['Shanghai Jiao Tong University', 'China', 'http://ftp.sjtu.edu.cn/ubuntu/', 'ftp.sjtu.edu.cn', ],
['University of Science and Technology', 'China', 'http://debian.ustc.edu.cn/ubuntu/', 'debian.ustc.edu.cn', ],
['University of Electronic Science and Technology', 'China', 'http://ubuntu.uestc.edu.cn/ubuntu/', 'ubuntu.uestc.edu.cn', ],
['Ubuntu Repository @ Peru', 'Peru', 'http://pe.archive.ubuntu.com/ubuntu/', 'pe.archive.ubuntu.com', ],
['Ubuntu Repository @ Ghana', 'Ghana', 'http://gh.archive.ubuntu.com/ubuntu/', 'gh.archive.ubuntu.com', ],
['Alfred State College', 'United States', 'http://mirror.alfredstate.edu/ubuntu/', 'mirror.alfredstate.edu', ],
['Ubuntu Repository @ Egypt', 'Egypt', 'http://eg.archive.ubuntu.com/ubuntu/', 'eg.archive.ubuntu.com' ],
]

def get_candidate_repositories():
    ret = []
    
    all_servers = set()
    for e in _g1() + _g2():
        assert len(e) ==4
        assert '://' in e[2]
        assert '.' in e[3], e
        server = e[3]
        if not server in all_servers:
            all_servers.add(server)
            ret.append(e)
    
    return ret
