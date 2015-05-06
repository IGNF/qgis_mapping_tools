from PyQt4.QtGui import QMessageBox

class Common:
    def __init__(self):
        pass
    
    def popup(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
