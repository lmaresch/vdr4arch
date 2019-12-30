#!/usr/bin/env python

#needs python-dateutil, python-pytz

import argparse
import datetime
from dateutil.parser import parse
import os
import pytz
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def info(text):
    print(bcolors.BOLD + bcolors.OKGREEN + str(datetime.datetime.now()) + ' INF: ' + bcolors.ENDC + bcolors.OKGREEN + str(text) + bcolors.ENDC)

def debug(text):
    if debugflag > 0:
        print(bcolors.BOLD + bcolors.OKBLUE + str(datetime.datetime.now()) + ' DBG: ' + bcolors.ENDC + bcolors.OKBLUE + str(text) + bcolors.ENDC)

def debug2(text):
    if debugflag > 1:
        print(bcolors.BOLD + bcolors.OKBLUE + str(datetime.datetime.now()) + ' DBG: ' + bcolors.ENDC + bcolors.OKBLUE + str(text) + bcolors.ENDC)

def warning(text):
    print(bcolors.BOLD + bcolors.WARNING + str(datetime.datetime.now()) + ' WRN: ' + bcolors.ENDC + bcolors.WARNING + str(text) + bcolors.ENDC)

def error(text):
    print(bcolors.BOLD + bcolors.FAIL + str(datetime.datetime.now()) + ' ERR: ' + bcolors.ENDC + bcolors.FAIL + str(text) + bcolors.ENDC)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='count', default=0)
args = parser.parse_args()

info('Synchronizing package lists...')
pacman = subprocess.run(['/usr/sbin/pacman', '-Sy'])
if pacman.returncode != 0:
    error('pacman -Sy failed with return code ' + str(pacman.returncode))

debugflag = args.debug
locallog = '/var/log/pacman.log'
logline = ''
debug('Reading lofgile \'' + locallog + '\'...')
with open(locallog, 'r') as logfile:
    for logline in reversed(list(logfile.readlines())):
        debug2(logline.replace(os.linesep, ''))
        if '[PACMAN] starting full system upgrade' in logline:
            break

lastupdate = logline[logline.index('[') + 1:logline.index(']')]
debug('Last update: ' + str(lastupdate))
dt = parse(lastupdate)
if (datetime.datetime.now() - datetime.timedelta(days=-1)).replace(tzinfo=None) > dt.replace(tzinfo=None):
    info('Last update done within the last day...')
else:
    warning('Last update older then one day, updating...')
    info('Upgrading system...')
    pacman = subprocess.run(['/usr/sbin/pacman', '-Su', '--noconfirm'])
    if pacman.returncode != 0:
        error('pacman -Su --noconfirm failed with return code ' + str(pacman.returncode))