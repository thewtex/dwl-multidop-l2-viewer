import os

from PyQt4 import QtCore, QtGui

from dwl_multidop_exceptions import *
from fileparsing.dwl_multidop_tx import TX
from fileparsing.dwl_multidop_tw import TW
from gui.dwl_main_window import DWLMainWindow

class DWLMainWindowController():
    def __init__(self, file_prefix):
        self.mw = DWLMainWindow()
        self.mw.show()

        self.load_file(file_prefix)

    def load_file(self, file_prefix):
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

        self.mw.setWindowTitle('DWL Multidop L2 Viewer - ' + tx_file)

        self.mw.statusBar().clearMessage()
        self.mw.statusBar().insertWidget(0, self.mw.loading_label)
        self.mw.statusBar().insertWidget(1, self.mw.loading_progress_bar)
        self.mw.loading_label.setText('Loading metadata .TX file...')
        self.mw.loading_label.show()
        self.mw.loading_progress_bar.show()

        self.tx = TX(tx_file, self.mw.loading_progress_bar)

        self.mw.loading_label.setText('Loading velocity data from .Tw FILE...')
        self.tw = TW(tw_file, self.tx.metadata['prf'], self.tx.metadata['doppler_freq_1'],
                self.tx.metadata['doppler_freq_2'], self.mw.loading_progress_bar)
        print self.tx.metadata
        self.mw.current_subject_label.setText('Current Patient: ' +
                self.tx.metadata['patient_name'])

        self.mw.statusBar().removeWidget(self.mw.loading_label)
        self.mw.statusBar().removeWidget(self.mw.loading_progress_bar)


