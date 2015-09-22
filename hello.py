#!/usr/bin/python2.7 -u
import os
import stat
import subprocess
import re

#ls && echo aa
try:
    subprocess.check_call(['ls'])
except subprocess.CalledProcessError:
    pass
else:
    try:
        subprocess.check_call(['echo', 'aa'])
    except subprocess.CalledProcessError:
        pass
    else:
        pass


#ls || echo aa
try:
    subprocess.check_call(['ls'])
except subprocess.CalledProcessError:
    try:
        subprocess.check_call(['echo', 'aa'])
    except subprocess.CalledProcessError:
        pass
    else:
        pass
else:
    pass


#ls || echo aa && echo bb
try:
    subprocess.check_call(['ls'])
except subprocess.CalledProcessError:
    try:
        subprocess.check_call(['echo', 'aa'])
    except subprocess.CalledProcessError:
        pass
    else:
        try:
            subprocess.check_call(['echo', 'bb'])
        except subprocess.CalledProcessError:
            pass
        else:
            pass
else:
    pass
