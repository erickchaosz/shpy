#!/usr/bin/python2.7 -u
import os
import stat

print stat.S_ISCHR(os.stat('/dev/null').st_mode)
