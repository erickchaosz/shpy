#!/usr/bin/python2.7 -u
import os
import stat
import subprocess


print stat.S_ISCHR(os.stat('/dev/null').st_mode)
print subprocess.check_output(['expr', '1', '+', '1'])
