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
_('''motto of Ailurus
Give a man a fish and he can eat for a day; but if you teach him how to fish, he'll eat for a lifetime.'''),

_('''Clear Bash history
history -c'''),

_('''If you want to use colorful "ls", that is, use colors to distinguish types of files, you can add these lines in ~/.bashrc:

if [ "$TERM" != "dumb" ]; then
    eval "`dircolors -b`"
    alias ls='ls --color=auto'
fi'''),

_('''Display Linux distributor's ID
lsb_release -is

Display Linux release number
lsb_release -rs

Display Linux code name
lsb_release -cs'''
  ),

_('''Display machine hardware name
uname -m'''),

_('''List all PCI devices, such as display card and ethernet card.
lspci
'''),

_('''Reclaim memory which stores pagecache, dentries and inodes
echo 3 > /proc/sys/vm/drop_caches
'''),

_("""Display a list of modules in the Linux Kernel
lsmod
"""),

_("""List USB devices
lsusb -v
"""),

_("""Display the status of ethernet card
sudo ethtool eth0
"""),

_("""List hardware
sudo lshw
"""),

_("""List harddisk partitions
sudo fdisk -l
"""),

_("""Display SATA harddisk parameters
sudo hdparm -I /dev/sda
"""),

_("""Display disk space usage
df -h
"""),

_("""Display file/folder space usage
du -bsh FOLDER_NAME
"""),

_("""Display amount of free and used memory
free
"""),

_("""Display processes
ps -e
Display a tree of processes
pstree
Display processes dynamically
top
"""),

_("""Terminate a process with a given process id
sudo kill -9 PROCESS_ID
"""),

_("""Terminate all processes with a given name
sudo killall PROCESS_NAME
"""),

_("""List files which are opened by a given process
lsof -p PROCESS_ID
lsof -c PROCESS_NAME
"""),

_("""List processes which opened a given file
lsof FILE_NAME
"""),

_("""List processes which are using port 80
lsof -i :80
"""),

_("""Configure an ADSL connection
sudo pppoeconf
"""),

_("""Starts up ADSL connections
sudo pon
Shuts down ADSL connections
sudo poff
"""),

_("""Display MAC of a given IP address
arping IP_ADDRESS
"""),

_("""Display NetBIOS name of a given IP address
nmblookup -A IP_ADDRESS
"""),

_("""Display IP address and MAC
ifconfig -a
"""),

_("""Display route
netstat -rn
"""),

_("""Set MAC of ethernet interface
sudo ifconfig eth0 hw ether 00:11:22:33:44:55
"""),

_("""Display information of a domain name
whois example.com
"""),

_("""Display the network path to a given host
tracepath example.com
"""),

_("""Request an IP address from DHCP server
sudo dhclient
"""),

_("""Temporarily restart an init script
sudo /etc/init.d/SCRIPT_NAME restart
Temporarily stop an init script
sudo /etc/init.d/SCRIPT_NAME stop
"""),

_("""Add a user
sudo adduser USER_NANE
Delete a user
sudo deluser USER_NAME
"""),

_("""Change user password
sudo passwd USER_NAME
"""),

_("""Changes user fullname, office number, office extension, and home phone number information.
sudo chfn USER_NAME
Display user information
finger USER_NAME
"""),

_("""Temporarily prevent a user from logging in
sudo usermod -L USER_NAME
Revoke the operation above
sudo usermod -U USER_NAME
"""),

_("""Add a user to admin group
sudo usermod -G admin -a USER_NAME
"""),

_("""Set the HTTP proxy
export http_proxy=http://PROXY.DOMAIN.NAME:PORT
"""),

_("""Modify the information displayed after logging in
sudo vim /etc/motd.tail
"""),

_("""Choose the input method for X Window
im-switch -c
"""),

_("""Convert the file name from GBK to UTF8
convmv -r -f gbk -t utf8 --notest FILE_NAME
"""),

_("""Convert the file content from GBK to UTF8
iconv -f gbk -t utf8 FILE_NAME
"""),

_("""Convert tags in '*.mp3' from GBK to UTF8
find . -name '*.mp3' -execdir mid3iconv -e GBK {} \;
"""),

_("""Read a long file
less FILE_NAME
"""),

_("""Print lines matching a pattern
grep REG_EXP FILE_NAME
"""),

_("""Display a list of file name. The files contain a given string.
grep -lr REG_EXP PATHNAME
"""),

_("""Display all '.txt' file
find . -name '*.txt'
"""),

_("""Create two empty files
touch file_name_1 file_name_2
"""),

_("""Create directory. Create parent directories as needed.
mkdir -p /tmp/a/b/c/d/e
"""),

_("""Change working directory to the home folder
cd
Change working directory to the previous working directory
cd -
"""),

_("""Display hidden files
ls -a
"""),

_("""Copy directory. Preserve links, file mode, ownership, timestamps. 
cp -a SOURCE_DIRECTORY DEST_DIRECTORY
"""),

_("""Determine file type
file FILE_NAME
"""),

_("""Output the last 6 lines
tail -n 6 FILE_NAME
"""),

_("""Copy files via SSH
scp -rp FILE_NAME USERNAME@HOST:DEST_PATH
"""),

_("""Rename '*.rm' files to '*.rmvb' files
rename 's/.rm$/.rmvb/' *
"""),

_("""Change the file name to lowercase
rename 'tr/A-Z/a-z/' *
"""),

_("""Display subdirectories in current directory
ls -d */.
"""),

_("""Display file number in current directory
ls . | wc -w
"""),

_("""Extract "*.gz" file
gunzip FILE_NAME.gz
Extract "*.tar.gz" file
tar zxf FILE_NAME.tar.gz
Extract "*.tar.bz2" file
tar jxf FILE_NAME.tar.bz2
"""),

_("""Do compression
tar czf FILE_NAME.tar.gz FILE1 FILE2 FILE3
tar cjf FILE_NAME.tar.bz2 FILE1 FILE2 FILE3
"""),

_("""Displays a calendar
cal
cal MONTH YEAR
"""),

_("""Set the date and time via NTP
sudo ntpdate ntp.ubuntu.com
"""),

_("""Poweroff your computer
sudo halt
sudo shutdown -h now
Poweroff your computer in 23:00
sudo shutdown -h 23:00
Poweroff your computer after 60 minutes
sudo shutdown -h +60
"""),

_("""Reboot your computer
sudo reboot
sudo shutdown -r now
"""),

_("""If you want some program to start up automatically, please put '.desktop' files into '~/.config/autostart'
"""),

_("""You can configure "preferred applications" by this file "~/.local/share/applications/mimeapps.list"
"""),

_("""Continuously monitor the memory usage
watch -d free
"""),

_("""Display HTTP HEAD response
w3m -dump_head http://example.com
"""),

_("""Display file content with line number
nl FILE_NAME
"""),

_("""Eliminate Rootkit
sudo rkhunter --checkall
"""),

_('''Change hostname
sudo hostname new_name
'''),

_('''"Tasksel" group software packages into "task"s. You can select a "task" and then install all necessary software packages. It is easy to set up LAMP servers or cloud computing servers.
Show all tasks
tasksel --list
Display the extended description of a task
tasksel --task-desc lamp-server
List the packages which are parts of a task
tasksel --task-packages lamp-server
Install/remove a task
gksudo tasksel
'''),

_('''Change Process priority
renice NEW_PRIORITY `pgrep NAME_OF_PROCESS`
example: renice 5  `pgrep firefox`     
         renice -5 `pgrep wine-server`       
               high <------------------> low
NEW_PRIORITY = -19, -18, -17 [...] 18, 19, 20
'''),

]
