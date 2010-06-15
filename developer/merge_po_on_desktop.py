#!/usr/bin/python

# In order to manually merge all "*.po" files from Launchpad translation
# Launchpad automatically sync translation to bzr every day.
# If you want this process be quicker, please run this script.

import os, sys, glob
po_path = os.path.expanduser('~/Desktop/po/')
assert os.path.exists(po_path)
workspace_path = os.path.expanduser('~/workspace/Ailurus/po/')
assert os.path.exists(workspace_path)

for file_path in glob.glob(po_path + '*.po'):
    src_file_name = os.path.split(file_path)[1]
    dest_file_name = src_file_name.replace('ailurus-', '')
    os.system('cp %s%s %s%s' % (po_path, src_file_name, workspace_path, dest_file_name))