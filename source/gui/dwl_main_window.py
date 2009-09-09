import os
import sys

from PyQt4 import QtCore, QtGui

import numpy

import veusz.setting
import veusz.windows.plotwindow 
import veusz.document as document

from gui.ui_dwl_main_window import Ui_DWLMainWindow
from gui.plot_window import DWLPlotWindow
from gui.plotting_logic import PlottingLogic

class DWLMainWindow(QtGui.QMainWindow):

    def __init__(self, file_prefix):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

        self._set_up_statusbar()
        self._set_up_menu()
        self.document = document.Document()
        self.plot = DWLPlotWindow(self.document, self)
        self.toolbar = self.plot.createToolbar(self, None)
        self.toolbar.show()
        self.setCentralWidget(self.plot)
        self.plotting_logic = PlottingLogic(self, self.document, file_prefix)


# print current x,y mouse position in lower left hand corner
        self.connect(self.plot, QtCore.SIGNAL("sigAxisValuesFromMouse"),
                self.slotUpdateAxisValues)

## 
# @brief set up the content of the bar at the bottom of the window
# 
# @return 
    def _set_up_statusbar(self):
        statusbar = self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(statusbar)
        self.statusBar().showMessage('Ready')
        self.current_subject_label = QtGui.QLabel(statusbar)
        self.statusBar().addPermanentWidget(self.current_subject_label)
        self.loading_label = QtGui.QLabel(statusbar)
        self.loading_progress_bar = QtGui.QProgressBar(statusbar)
        self.axis_values_label = QtGui.QLabel(statusbar)
        statusbar.addWidget(self.axis_values_label)
        self.axis_values_label.show()

## 
# @brief set up the menu bar at the top
# 
# @return 
    def _set_up_menu(self):
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu('&File')

        open_action = QtGui.QAction(QtGui.QIcon('icons/open.png'), '&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open different fileset')
        self.connect(open_action, QtCore.SIGNAL('triggered()'), self.open_file)
        self.file_menu.addAction(open_action)

        self.exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Quit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.connect(self.exit_action, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.file_menu.addAction(self.exit_action)

        self.show()

## 
# @brief bring up a file open dialog and load in the requestd data set
# 
# @return 
    def open_file(self):
        fileprefix = QtGui.QFileDialog.getOpenFileName(None, "Select *.TX0 or *.TW0 file.", 
                os.getcwd(), 
                ("DWL MultiDop L2 Files (*.TX? *.TW? *.tx? *.tw?)"))
        fileprefix = str(fileprefix)
        self.plotting_logic.load_file(fileprefix)


    def slotUpdateAxisValues(self, values):
        """Update the position where the mouse is relative to the axes."""

        if values:
            # construct comma separated text representing axis values
            valitems = []
            for name, val in values.iteritems():
                valitems.append('%s=%#.4g' % (name, val))
            valitems.sort()
            self.axis_values_label.setText(', '.join(valitems))
        else:
            self.axis_values_label.setText('No position')

