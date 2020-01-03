#!/usr/bin/env python

#needs python-dateutil, python-pytz

import argparse
import datetime
from dateutil.parser import parse
import os
import pytz
import subprocess
import sys

class Pkgbuild:
    def __init__(self, pkgbuildpath):
        super().__init__()
        self.pkgbuildpath = pkgbuildpath
        self.pkgname = ''
        self.pkgdesc = ''
        self.pkgver = ''
        self.pkgrel = ''
        self.archs = []
        self.conflicts = []
        self.depends = []
        self.optdepends = []
        self.makedepends = []
        self.unknownparams = dict()
        self.ignoredparams = ['source', 'sha256sums', 'md5sums', 'sha512sums', 'install', 'backup', 'url', 'license']
        self.packagefilename = ''
        self.packagedebugfilename = ''
    def parsefile(self):
        try:
            debug('Parsing file {0}...'.format(self.pkgbuildpath))
            with open(self.pkgbuildpath, 'r') as f:
                for line in f.readlines():
                    debug2('Parsing line: {0}'.format(line.replace(os.linesep, '')))
                    if not line.strip() or line[:1] == '#' or not '=' in line or line[:line.index('=')] in self.ignoredparams:
                        continue
                    if line.startswith('pkgname'):
                        self.pkgname = line[line.index('=') + 1:]
                    elif line.startswith('pkgdesc'):
                        self.pkgdesc = line[line.index('=') + 1:]
                    elif line.startswith('pkgver'):
                        self.pkgver = line[line.index('=') + 1:]
                    elif line.startswith('pkgrel'):
                        self.pkgrel = line[line.index('=') + 1:]
                    elif line.startswith('arch'):
                        for entry in line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').split(' '):
                            self.archs.append(entry)
                    elif line.startswith('depends'):
                        for entry in line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').split(' '):
                            self.depends.append(entry)
                    elif line.startswith('conflicts'):
                        for entry in line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').split(' '):
                            self.conflicts.append(entry)
                    elif line.startswith('optdepends'):
                        for entry in line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').split(' '):
                            self.optdepends.append(entry)
                    elif line.startswith('makedepends'):
                        for entry in line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').split(' '):
                            self.makedepends.append(entry)
                    else:
                        self.unknownparams.update({line[:line.index('=')]: line[line.index('=') + 1:]})                
        except IOError as e:
            error('I/O error({0}): {1}'.format(e.errno, e.strerror))
            return False
        except:
            error('Unexpected error: ' + sys.exc_info()[0])
            return False
        if '$' in self.pkgname:
            self.pkgname = self._evaluatevariables(self.pkgname)
        if '$' in self.pkgdesc:
            self.pkgdesc = self._evaluatevariables(self.pkgdesc)
        if '$' in self.pkgver:
            self.pkgver = self._evaluatevariables(self.pkgver)
        if '$' in self.pkgrel:
            self.pkgrel = self._evaluatevariables(self.pkgrel)
        for entry in self.archs:
            if '$' in entry:
                entry = self._evaluatevariables(entry)
        for entry in self.depends:
            if '$' in entry:
                entry = self._evaluatevariables(entry)
        for entry in self.conflicts:
            if '$' in entry:
                entry = self._evaluatevariables(entry)
        for entry in self.optdepends:
            if '$' in entry:
                entry = self._evaluatevariables(entry)
        for entry in self.makedepends:
            if '$' in entry:
                entry = self._evaluatevariables(entry)
        return True
    
    def _evaluatevariables(self, value):
        prefix = '$'
        varname = ''
        postfix = ''
        pos = value.index(prefix) + 1
        if value[pos] == '{':
            prefix = '${'
            postfix = '}'
        for entry in self.unknownparams:
            if prefix + entry + postfix in value:
                value.replace(prefix + entry + postfix, self.unknownparams[entry])
        return value

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

def readmakepkgconf():
    makepkgconf = '/etc/makepkg.conf'
    info('Reading {0}...'.format(makepkgconf))
    config = dict()
    try:
        with open(makepkgconf, 'r') as f:
            for line in f.readlines():
                debug2('Linecontent: {0}'.format(line.replace('\n', '')))
                if not line.strip() or line[:1] == '#':
                    debug2('--> Line is ignored as it is empty or starts with a \'#\'')
                    continue
                if line.startswith('CARCH') or line.startswith('PKGEXT') or line.startswith('BUILDDIR') or line.startswith('SRCDEST') or line.startswith('BUILDENV'):
                    debug2('Key/value pair \'{0}\':\'{1}\' added to dict'.format(line[:line.index('=')].strip(), line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').strip()))
                    config.update({line[:line.index('=')].strip(): line[line.index('=') + 1:].replace('(', '').replace(')', '').replace("'", '').replace('"', '').strip()})
    except IOError as e:
        error('I/O error({0}): {1}'.format(e.errno, e.strerror))
        exit(1)
    except:
        error('Unexpected error in {0}: '.format(str(__name__)) + sys.exc_info()[0])
        exit(1)
    return config

def getentriesfromrepomakeconf(repomakefile):
    pkgbuildfiles = []
    try:
        info('Reading file \'' + repomakeconf + '\'...')
        with open(repomakeconf, 'r') as repomakefile:
            for repomakeline in repomakefile.readlines():
                debug2('Linecontent: {0}'.format(repomakeline.replace('\n', '')))
                if not repomakeline.strip() or repomakeline[:1] == '#':
                    debug2('--> Line is ignored as it is empty or starts with a \'#\'')
                    continue
                if '=' in repomakeline:
                    debug2('--> Line is ignored as it contains a \'=\'')
                    continue
                debug2('--> Line added to array for processing')
                pkgbuildfiles.append(repomakeline.replace(os.linesep, ''))
    except IOError as e:
        error('I/O error({0}): {1}'.format(e.errno, e.strerror))
        exit(1)
    except:
        error('Unexpected error in {0}: '.format(str(__name__)) + sys.exc_info()[0])
        exit(1)
    return pkgbuildfiles

def analyzepkgbuildfiles(pkgbuildfiles):
    pkgbuilds = []
    try:
        info('Processing {0} entries...'.format(len(pkgbuildfiles)))
        for pkgbuildfile in pkgbuildfiles:
            fullpath = os.path.join(str(builddir), str(pkgbuildfile), 'PKGBUILD')
            if not os.path.exists(fullpath):
                warning('File {0} doesn\'t exist, ignoring...'.format(fullpath))
                continue
            pkgbuildentry = Pkgbuild(fullpath)
            if not pkgbuildentry.parsefile():
                warning('Could not parse file {0}'.format(fullpath))
                continue
            pkgbuilds.append(pkgbuildentry)
    except IOError as e:
        error('I/O error({0}): {1}'.format(e.errno, e.strerror))
        exit(1)
    except:
        error('Unexpected error in {0}: '.format(str(__name__)) + sys.exc_info()[0])
        exit(1)
    return pkgbuilds

parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='count', default=0)
parser.add_argument('--directory', '-D', action='store', default=os.getcwd())
args = parser.parse_args()

debugflag = args.debug
builddir = args.directory

makepkgconf = readmakepkgconf()
debug('makepkgconf: {0}'.format(str(makepkgconf)))
repomakeconf = 'repo-make.conf'
pkgbuildfiles = getentriesfromrepomakeconf(repomakeconf)
pkgbuilds = analyzepkgbuildfiles(pkgbuildfiles)


#info('Synchronizing package lists...')
#pacman = subprocess.run(['/usr/sbin/pacman', '-Sy'])
#if pacman.returncode != 0:
#    error('pacman -Sy failed with return code ' + str(pacman.returncode))

#locallog = '/var/log/pacman.log'
#logline = ''
#debug('Reading lofgile \'' + locallog + '\'...')
#with open(locallog, 'r') as logfile:
#    for logline in reversed(list(logfile.readlines())):
#        debug2(logline.replace(os.linesep, ''))
#        if '[PACMAN] starting full system upgrade' in logline:
#            break

#lastupdate = logline[logline.index('[') + 1:logline.index(']')]
#debug('Last update: ' + str(lastupdate))
#dt = parse(lastupdate)
#if (datetime.datetime.now() - datetime.timedelta(days=-1)).replace(tzinfo=None) > dt.replace(tzinfo=None):
#    info('Last update done within the last day...')
#else:
#    warning('Last update older then one day, updating...')
#    info('Upgrading system...')
#    pacman = subprocess.run(['/usr/sbin/pacman', '-Su', '--noconfirm'])
#    if pacman.returncode != 0:
#        error('pacman -Su --noconfirm failed with return code ' + str(pacman.returncode))

