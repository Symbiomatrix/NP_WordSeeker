import design_exp
from PyQt5 import QtCore, QtGui, QtWidgets 

import sys

class MainApp(QtWidgets.QMainWindow, design_exp.Ui_MainWindow):
    appname = "Main" 
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined
                            
        # Hiding must be done in runtime,
        # since qt designer voluntarily removed the visible prop.
        self.textBrowser_11.hide()

FORMDIR = dict()

app = QtWidgets.QApplication(sys.argv)
FORMDIR["Main"] = MainApp()
FORMDIR["Main"].show()
try:
    app.exec_()
except Exception as err: # Not very useful, since the gui hangs after uncaught action.
    indcrash = True
    print("Crashed")
    raise
