#!/usr/bin/python2.7 -u
import os
import stat
import subprocess
import re

text = '$((1 + 1))'
regex = re.compile(r'(\$\(\()\s+')
match = regex.match(text, 0)
print match.group(1)
print match.end(1)
