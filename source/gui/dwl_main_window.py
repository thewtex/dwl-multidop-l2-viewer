from PyQt4 import QtCore, QtGui

from gui.ui_dwl_main_window import Ui_DWLMainWindow

class DWLMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

        self.statusBar().showMessage('Ready')

        self.current_file_label = QtGui.QLabel(self.statusBar())
        self.current_file_label.setText("Hey some text")
        self.statusBar().addPermanentWidget(self.current_file_label)
