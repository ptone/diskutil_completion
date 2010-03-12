#!/usr/bin/env python
# encoding: utf-8
"""
This script is called by a bash completion function to help complete 
the options for the diskutil os x command

Created by Preston Holmes on 2010-03-11.
preston@ptone.com
Copyright (c) 2010

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import os
from subprocess import Popen, call, STDOUT, PIPE
import plistlib
import re

cache = '/tmp/completiondiskcache'
DEBUG = True
USE_CACHE = False

def sh(cmd):
    return Popen(cmd,shell=True,stdout=PIPE,stderr=PIPE).communicate()[0]

def debug(msg):
    if DEBUG:
        f = open ('/tmp/completedebug','a')
        f.write (str(msg) + '\n')
        f.close()

def get_disks(curr=''):
    if USE_CACHE and os.path.exists(cache):
        diskinfo = plistlib.readPlist(cache)
    else:
        diskinfo = plistlib.readPlistFromString(sh("diskutil list -plist"))
        if USE_CACHE:
            plistlib.writePlist(diskinfo,cache)
    named_disk_ct = len(diskinfo['VolumesFromDisks'])
    opts = []
    for i,d in enumerate(diskinfo['WholeDisks']):
        o = "/dev/%s" % d
        if i < named_disk_ct:
            o += "(%s)" % diskinfo['VolumesFromDisks'][i].replace(' ','_')
        if curr:
            if o.startswith(curr):
                opts.append(o)
        else:
            opts.append(o)
    if len(opts) == 1 and '(' in opts[0]:
        opts[0] = opts[0].split('(')[0]
    debug ("disks:");debug(opts)
    return opts

def re_in(pat,l):
    r = re.compile(pat)
    contained = [x for x in l if r.search(x)]
    return len(contained)

def complete():
    """ note if compreply only gets one word it will fully complete"""
    verbs = """
            list
            info
            unmount
            unmountDisk
            eject
            mount
            mountDisk
            rename
            enableJournal
            disableJournal
            verifyVolume
            repairVolume
            verifyPermissions
            repairPermissions
            eraseVolume
            eraseOptical
            zeroDisk
            randomDisk
            secureErase
            partitionDisk
            resizeVolume
            splitPartition
            mergePartition
            """.split()
    verbs_for_device = """        
            list
            info
            unmount
            unmountDisk
            eject
            mount
            mountDisk
            rename
            enableJournal
            disableJournal
            verifyVolume
            repairVolume
            verifyPermissions
            repairPermissions
            eraseVolume
            eraseOptical
            zeroDisk
            randomDisk
            secureErase
            partitionDisk
            resizeVolume
            splitPartition
            mergePartition
            """.split()
    device_final = """        
            list
            info
            unmount
            unmountDisk
            eject
            mount
            mountDisk
            enableJournal
            disableJournal
            verifyVolume
            repairVolume
            verifyPermissions
            repairPermissions
            eraseVolume
            eraseOptical
            zeroDisk
            randomDisk
            secureErase
            """.split()
    verb_options = {
            "list":('-plist', ),
            "info":('-plist', ),
            "unmount":('force', ),
            "unmountDisk":('force', ),
            "eject":( ),
            "mount":('readOnly', ),
            "mountDisk":( ),
            "rename":('<name>', ),
            "enableJournal":( ),
            "disableJournal":('force', ),
            "verifyVolume":( ),
            "repairVolume":( ),
            "verifyPermissions":('-plist', ),
            "repairPermissions":('-plist', ),
            "eraseVolume":(
                "Journaled_HFS+",
                "HFS+",
                "Case-sensitive_HFS+",
                "Case-sensitive_Journaled_HFS+",
                "HFS",
                "MS-DOS_FAT16",
                "MS-DOS_FAT32",
                "MS-DOS_FAT12",
                "MS-DOS",
                "UDF",
                "UFS",
                "ZFS",'<name>' ),
            "eraseOptical":('quick', ),
            "zeroDisk":( ),
            "randomDisk":('<times>', ),
            "secureErase":( ),
            "partitionDisk":( ),
            "resizeVolume":( ),
            "splitPartition":( ),
            "mergePartition":( )
            }
    cwords = os.environ['COMP_WORDS'].split()[1:]
    cword = int(os.environ['COMP_CWORD'])
    debug(cword)
    
    try:
        curr = cwords[cword-1]
    except IndexError:
        curr = ''
    debug("current: " + curr)
    if cword == 1:
        if os.path.exists(cache):
            os.remove(cache)
        opts = verbs
    elif cwords[0] in verbs:
        opts = []
        if cwords[0] in verbs_for_device:
            # if verb has device as last param - and dev is last word, exit
            if cword != len(cwords) and '/dev' in cwords[-1]:
                sys.exit(0)
            if not re_in('/dev',cwords) or '/dev' in curr:
                opts.extend(get_disks(curr))
        opts.extend(verb_options[cwords[0]])
        opts = [x for x in opts if x not in cwords[:-2]]
        debug(opts)
        debug (cwords)
    print ' '.join(filter(lambda x: x.lower().startswith(curr.lower()), opts))
    debug ("final %s" % ' '.join(filter(lambda x: x.startswith(curr), opts)))
    sys.exit(0)
def main():
    complete()    
if __name__ == '__main__':
    main()

