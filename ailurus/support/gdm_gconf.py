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

# Write result to /tmp/output
# Write error to /tmp/error

from __future__ import with_statement
import os, sys, subprocess
assert len(sys.argv) > 1

def get_gdm_uid():
    import pwd
    for item in pwd.getpwall():
        if item.pw_name == 'gdm': return item.pw_uid
    else:
        raise Exception('gdm not found in /etc/passwd')

uid = get_gdm_uid()
os.setuid(uid)
task = subprocess.Popen(['gconftool-2'] + sys.argv[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
with open('/tmp/output', 'w') as f:
    f.write(task.stdout.read())
with open('/tmp/error', 'w') as f:
    f.write(task.stderr.read())
task.wait()
assert task.returncode == 0