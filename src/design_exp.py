# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Itai\Programming\Python\Winpy365\Projects\Qtui\TestCheckboard.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(110, 50, 381, 431))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.textBrowser_11 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_11.setObjectName("textBrowser_11")
        self.gridLayout.addWidget(self.textBrowser_11, 1, 4, 1, 1)
        self.textBrowser_17 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_17.setObjectName("textBrowser_17")
        self.gridLayout.addWidget(self.textBrowser_17, 4, 3, 1, 1)
        self.textBrowser_13 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_13.setObjectName("textBrowser_13")
        self.gridLayout.addWidget(self.textBrowser_13, 2, 3, 1, 1)
        self.textBrowser_16 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_16.setObjectName("textBrowser_16")
        self.gridLayout.addWidget(self.textBrowser_16, 3, 4, 1, 1)
        self.textBrowser_7 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_7.setObjectName("textBrowser_7")
        self.gridLayout.addWidget(self.textBrowser_7, 1, 2, 1, 1)
        self.textBrowser_5 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_5.setObjectName("textBrowser_5")
        self.gridLayout.addWidget(self.textBrowser_5, 3, 0, 1, 1)
        self.textBrowser_9 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_9.setObjectName("textBrowser_9")
        self.gridLayout.addWidget(self.textBrowser_9, 3, 2, 1, 1)
        self.textBrowser_10 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_10.setObjectName("textBrowser_10")
        self.gridLayout.addWidget(self.textBrowser_10, 4, 1, 1, 1)
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.gridLayout.addWidget(self.textBrowser_2, 1, 0, 1, 1)
        self.textBrowser_4 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_4.setObjectName("textBrowser_4")
        self.gridLayout.addWidget(self.textBrowser_4, 2, 1, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 0, 1, 1, 1)
        self.textBrowser_12 = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser_12.setObjectName("textBrowser_12")
        self.gridLayout.addWidget(self.textBrowser_12, 0, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 200, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(550, 80, 104, 71))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(550, 170, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(540, 240, 47, 13))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
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
        self.label.setText(_translate("MainWindow", "TextLabel"))


