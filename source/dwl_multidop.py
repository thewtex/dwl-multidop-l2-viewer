#!/usr/bin/env python

import glob
import os
import sys

from PyQt4 import QtGui, QtCore
app = QtGui.QApplication(sys.argv)

from dwl_multidop_exceptions import *
from fileparsing.dwl_multidop_tx import TX
from fileparsing.dwl_multidop_tw import TW
from gui.dwl_main_window_controller import DWLMainWindowController

def main(file_prefix):
    filepath = file_prefix
    if not os.path.isabs(file_prefix):
        filepath = os.path.abspath(file_prefix)
    tx_file = None
    tw_file = None
    if filepath[-2:] == '.t' or filepath[-2:] == '.T':
        filepath = filepath[:-2]
        tx_file = glob.glob(filepath + '.[Tt][Xx][0-9]')
        tw_file = glob.glob(filepath + '.[Tt][Ww][0-9]')
        if len(tx_file) > 1:
            print "More than one file encounterd; please specify full path."
            sys.exit(1)
    elif filepath[-4:-1] == '.tx' or filepath[-4:-1] == '.TX':
        tx_file = filepath
        other_file = filepath[:-1] + 'w' + filepath[-1:]
        if not os.path.exists(other_file):
            other_file = filepath[:-2] + 'W' + filepath[-1:]
        tw_file = other_file
    elif filepath[-4:-1] == '.tw' or filepath[-4:-1] == '.TW':
        tw_file = filepath
        other_file = filepath[:-1] + 'x' + filepath[-1:]
        if not os.path.exists(other_file):
            other_file = filepath[:-2] + 'X' + filepath[-1:]
        tx_file = other_file


    if not tw_file or not tx_file or tx_file[-1] == 't':
        e = ExtensionError(file_prefix, '.tx? and .tw? or .TX? and .TW?')
        raise e
        pass

    tx = TX(tx_file)
    tw = TW(tw_file, tx.metadata['prf'], tx.metadata['doppler_freq_1'],
            tx.metadata['doppler_freq_2'])
    print tx.metadata

    main_window_controller = DWLMainWindowController(tx_file,
            tx.metadata['patient_name'])
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
