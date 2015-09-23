#!/usr/bin/python2.7 -u
import os
import stat
import subprocess
import re

# cat < file >> file2




with open('test2', 'a') as f:
    print >>f, subprocess.check_output(['echo', 'a'])

with open('test', 'r') as f:
    subprocess.call(['cat'], stdin=f)
