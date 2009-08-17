from PyQt4 import QtCore, QtGui

from gui.ui_dwl_main_window import Ui_DWLMainWindow

class DWLMainWindow(QtGui.QMainWindow):
    def __init__(self):
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
        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
