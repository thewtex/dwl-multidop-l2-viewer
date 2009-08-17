from gui.dwl_main_window import DWLMainWindow

class DWLMainWindowController():
    def __init__(self, current_file, current_patient):
        self.mw = DWLMainWindow(current_file, current_patient)
        self.mw.show()


