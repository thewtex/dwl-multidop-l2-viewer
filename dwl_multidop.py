#!/usr/bin/env python

import sys

usage = """usage: %prog [options] <fileprefix>

<fileprefix> is the filename prefix of the DWL Multidop L2 files.

E.g., if you have 'nla168.TX0' and 'nla168.TW0'
in the current directory <fileprefix> = 'nla168'"""

if len(sys.argv) > 2:
    print usage
    sys.exit(1)

