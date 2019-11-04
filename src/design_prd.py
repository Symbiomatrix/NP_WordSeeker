# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Itai\Programming\Python\Winpy365\Projects\Qtui\Wordseeker.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(934, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 10, 441, 411))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(490, 10, 221, 366))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblRes1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lblRes1.setObjectName("lblRes1")
        self.verticalLayout.addWidget(self.lblRes1)
        self.lstRes1 = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.lstRes1.setObjectName("lstRes1")
        self.verticalLayout.addWidget(self.lstRes1)
        self.lblRes2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.lblRes2.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.lblRes2.setObjectName("lblRes2")
        self.verticalLayout.addWidget(self.lblRes2)
        self.lstRes2 = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.lstRes2.setObjectName("lstRes2")
        self.verticalLayout.addWidget(self.lstRes2)
        self.cmdNew = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdNew.setObjectName("cmdNew")
        self.verticalLayout.addWidget(self.cmdNew)
        self.cmdCan = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdCan.setObjectName("cmdCan")
        self.verticalLayout.addWidget(self.cmdCan)
        self.cmdUpd = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdUpd.setObjectName("cmdUpd")
        self.verticalLayout.addWidget(self.cmdUpd)
        self.cmdStep = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdStep.setObjectName("cmdStep")
        self.verticalLayout.addWidget(self.cmdStep)
        self.cmdParti = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdParti.setObjectName("cmdParti")
        self.verticalLayout.addWidget(self.cmdParti)
        self.cmdDrop = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cmdDrop.setObjectName("cmdDrop")
        self.verticalLayout.addWidget(self.cmdDrop)
        self.txtHiddenTest = QtWidgets.QLineEdit(self.centralwidget)
        self.txtHiddenTest.setEnabled(True)
        self.txtHiddenTest.setGeometry(QtCore.QRect(490, 390, 113, 20))
        self.txtHiddenTest.setStyleSheet("background-color: rgba(255,0,0,50)")
        self.txtHiddenTest.setObjectName("txtHiddenTest")
        self.txtGrid = QtWidgets.QTextEdit(self.centralwidget)
        self.txtGrid.setGeometry(QtCore.QRect(720, 30, 111, 181))
        self.txtGrid.setPlaceholderText("")
        self.txtGrid.setObjectName("txtGrid")
        self.txtGtype = QtWidgets.QLineEdit(self.centralwidget)
        self.txtGtype.setGeometry(QtCore.QRect(720, 250, 113, 20))
        self.txtGtype.setObjectName("txtGtype")
        self.lblGrid = QtWidgets.QLabel(self.centralwidget)
        self.lblGrid.setGeometry(QtCore.QRect(720, 10, 111, 16))
        self.lblGrid.setObjectName("lblGrid")
        self.lblGtype = QtWidgets.QLabel(self.centralwidget)
        self.lblGtype.setGeometry(QtCore.QRect(720, 230, 111, 16))
        self.lblGtype.setObjectName("lblGtype")
        self.lblDiff = QtWidgets.QLabel(self.centralwidget)
        self.lblDiff.setGeometry(QtCore.QRect(720, 280, 111, 16))
        self.lblDiff.setObjectName("lblDiff")
        self.txtDiff = QtWidgets.QLineEdit(self.centralwidget)
        self.txtDiff.setGeometry(QtCore.QRect(720, 300, 113, 20))
        self.txtDiff.setObjectName("txtDiff")
        self.lblDubstep = QtWidgets.QLabel(self.centralwidget)
        self.lblDubstep.setGeometry(QtCore.QRect(720, 320, 101, 31))
        self.lblDubstep.setWordWrap(True)
        self.lblDubstep.setObjectName("lblDubstep")
        self.txtDubstep = QtWidgets.QLineEdit(self.centralwidget)
        self.txtDubstep.setGeometry(QtCore.QRect(720, 350, 113, 20))
        self.txtDubstep.setObjectName("txtDubstep")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 934, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.lblRes1.setText(_translate("MainWindow", "High score"))
        self.lblRes2.setText(_translate("MainWindow", "Longevity"))
        self.cmdNew.setText(_translate("MainWindow", "Reset / new board"))
        self.cmdCan.setText(_translate("MainWindow", "Rollback changes"))
        self.cmdUpd.setText(_translate("MainWindow", "Commit changes"))
        self.cmdStep.setText(_translate("MainWindow", "Step through chain"))
        self.cmdParti.setText(_translate("MainWindow", "Partition selection"))
        self.cmdDrop.setText(_translate("MainWindow", "Select combo and drop"))
        self.txtHiddenTest.setText(_translate("MainWindow", "Sample tile."))
        self.txtGrid.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">2,3,5,5,5,5,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3,1,2,3,3,2,4,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">4,2,1,4,1,3,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3,4,2,5,5,3,3,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3,5,2,2,4,2,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3,2,2,2,1,1,5,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">5,2,3,1,5,4,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3,4,1,1,1,4,3,</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">4,4,5,5,4,1 .</span></p></body></html>"))
        self.txtGtype.setText(_translate("MainWindow", "2"))
        self.lblGrid.setText(_translate("MainWindow", "Grid base layout"))
        self.lblGtype.setText(_translate("MainWindow", "Game type"))
        self.lblDiff.setText(_translate("MainWindow", "Number difference"))
        self.txtDiff.setText(_translate("MainWindow", "1"))
        self.lblDubstep.setText(_translate("MainWindow", "Auto step (in ms and 0 = manual)"))
        self.txtDubstep.setText(_translate("MainWindow", "1000"))


