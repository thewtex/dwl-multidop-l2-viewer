#!/usr/bin/env python

import glob
import os
import sys

from veusz.setting.settingdb import settingdb
settingdb.readSettings()

from PyQt4 import QtGui, QtCore
app = QtGui.QApplication(sys.argv)

from gui.dwl_main_window_controller import DWLMainWindowController

def main(file_prefix):
    main_window_controller = DWLMainWindowController(file_prefix)
    sys.exit(app.exec_())


if __name__ == '__main__':
    usage = """usage: %prog [options] <fileprefix>

    <fileprefix> is the filename prefix of the DWL Multidop L2 files.

    E.g., if you have 'nla168.TX0' and 'nla168.TW0'
    in the current directory <fileprefix> = 'nla168'"""

    fileprefix = None
    if len(sys.argv) > 2:
        print usage
        sys.exit(1)
    elif len(sys.argv) == 2:
        fileprefix = sys.argv[1]
    else:
        fileprefix = QtGui.QFileDialog.getOpenFileName(None, "Select *.TX0 or *.TW0 file.", 
                os.getcwd(), 
                ("DWL MultiDop L2 Files (*.TX? *.TW? *.tx? *.tw?)"))
        fileprefix = str(fileprefix)

    main(fileprefix)
