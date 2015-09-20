#!/usr/bin/python2.7 -u
import os
import stat
import subprocess
import re

text = 'echo echon'
regex = re.compile(r'(echo)\s+')
match = regex.match(text, 0)
print match.group(0)
print match.end(1)
