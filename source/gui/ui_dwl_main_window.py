# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dwl_main_window.ui'
#
# Created: Mon Aug 17 02:07:59 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DWLMainWindow(object):
    def setupUi(self, DWLMainWindow):
        DWLMainWindow.setObjectName("DWLMainWindow")
        DWLMainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(DWLMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        DWLMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(DWLMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        DWLMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(DWLMainWindow)
        self.statusbar.setObjectName("statusbar")
        DWLMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(DWLMainWindow)
        QtCore.QMetaObject.connectSlotsByName(DWLMainWindow)

    def retranslateUi(self, DWLMainWindow):
        DWLMainWindow.setWindowTitle(QtGui.QApplication.translate("DWLMainWindow", "DWL Multidop L2 Viewer", None, QtGui.QApplication.UnicodeUTF8))

