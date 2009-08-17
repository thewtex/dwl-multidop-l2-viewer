from PyQt4 import QtCore, QtGui

from gui.ui_dwl_main_window import Ui_DWLMainWindow

class DWLMainWindow(QtGui.QMainWindow):
    def __init__(self, current_file, current_patient):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_DWLMainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('DWL Multidop L2 Viewer - ' + current_file)

# set up status bar
        self.statusBar().showMessage('Ready')
        self.current_subject_label = QtGui.QLabel(self.statusBar())
        self.current_subject_label.setText('Current Patient: ' + current_patient)
        self.statusBar().addPermanentWidget(self.current_subject_label)
