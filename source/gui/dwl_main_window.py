import os
import sys

from PyQt4 import QtCore, QtGui

import veusz.windows.plotwindow 
import veusz.document as document
from veusz.document.commandinterface import CommandInterface

from dwl_multidop_exceptions import *
from fileparsing.dwl_multidop_tx import TX
from fileparsing.dwl_multidop_tw import TW
from gui.ui_dwl_main_window import Ui_DWLMainWindow

class DWLMainWindow(QtGui.QMainWindow):
    def __init__(self, file_prefix):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

# set up status bar
        self.statusBar().showMessage('Ready')
        self.current_subject_label = QtGui.QLabel(self.statusBar())
        self.statusBar().addPermanentWidget(self.current_subject_label)
        self.loading_label = QtGui.QLabel(self.statusBar())
        self.loading_progress_bar = QtGui.QProgressBar(self.statusBar())

# set up menu
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')

        self.exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Quit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.connect(self.exit_action, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.file_menu.addAction(self.exit_action)

        open_action = QtGui.QAction(QtGui.QIcon('icons/open.png'), '&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open different fileset')
        self.connect(open_action, QtCore.SIGNAL('triggered()'), self.open_file)
        self.file_menu.addAction(open_action)

# set up graph
        self.document = document.Document()
        self.plot = veusz.windows.plotwindow.PlotWindow(self.document, self)
        self.toolbar = self.plot.createToolbar(self, None)
        self.toolbar.show()
        self.setCentralWidget(self.plot)
        self.i = CommandInterface(self.document)
        self.i.To(self.i.Add('page'))
        self.i.To(self.i.Add('graph'))
        self.plot.slotViewZoomPage()


        self.show()

        self.load_file(file_prefix)


## 
# @brief read in the data from the .tx and tw files
# 
# @param file_prefix prefix to the files
# 
# @return 
    def load_file(self, file_prefix):
# find the filepath
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

        self.setWindowTitle('DWL Multidop L2 Viewer - ' + tx_file)

# load tx file
        self.statusBar().clearMessage()
        self.statusBar().insertWidget(0, self.loading_label)
        self.statusBar().insertWidget(1, self.loading_progress_bar)
        self.loading_label.setText('Loading metadata .TX file...')
        self.loading_label.show()
        self.loading_progress_bar.show()

        self.tx = TX(tx_file, self.loading_progress_bar)

# load tw file
        self.loading_label.setText('Loading velocity data from .TW FILE...')
        self.tw = TW(tw_file, self.tx.metadata['prf'], self.tx.metadata['doppler_freq_1'],
                self.tx.metadata['doppler_freq_2'], self.loading_progress_bar)
        print self.tx.metadata
        self.current_subject_label.setText('Current Patient: ' +
                self.tx.metadata['patient_name'])

        self.statusBar().removeWidget(self.loading_label)
        self.statusBar().removeWidget(self.loading_progress_bar)

## 
# @brief bring up a file open dialog and load in the requestd data set
# 
# @return 
    def open_file(self):
        fileprefix = QtGui.QFileDialog.getOpenFileName(None, "Select *.TX0 or *.TW0 file.", 
                os.getcwd(), 
                ("DWL MultiDop L2 Files (*.TX? *.TW? *.tx? *.tw?)"))
        fileprefix = str(fileprefix)
        self.load_file(fileprefix)

