# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DEMO\Documents\dev\pickLayer\ui_changeDSDialog.ui'
#
# Created: Fri Oct 17 15:16:55 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_changeDataSourceDialog(object):
    def setupUi(self, changeDataSourceDialog):
        changeDataSourceDialog.setObjectName(_fromUtf8("changeDataSourceDialog"))
        changeDataSourceDialog.resize(657, 127)
        self.buttonBox = QtGui.QDialogButtonBox(changeDataSourceDialog)
        self.buttonBox.setGeometry(QtCore.QRect(300, 80, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(changeDataSourceDialog)
        self.label.setGeometry(QtCore.QRect(120, 20, 171, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineEdit = QtGui.QLineEdit(changeDataSourceDialog)
        self.lineEdit.setGeometry(QtCore.QRect(116, 40, 531, 22))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.selectDatasourceCombo = QtGui.QComboBox(changeDataSourceDialog)
        self.selectDatasourceCombo.setGeometry(QtCore.QRect(10, 40, 101, 22))
        self.selectDatasourceCombo.setObjectName(_fromUtf8("selectDatasourceCombo"))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.selectDatasourceCombo.addItem(_fromUtf8(""))
        self.label_2 = QtGui.QLabel(changeDataSourceDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.openBrowser = QtGui.QPushButton(changeDataSourceDialog)
        self.openBrowser.setGeometry(QtCore.QRect(605, 41, 41, 20))
        self.openBrowser.setObjectName(_fromUtf8("openBrowser"))

        self.retranslateUi(changeDataSourceDialog)
        QtCore.QMetaObject.connectSlotsByName(changeDataSourceDialog)

    def retranslateUi(self, changeDataSourceDialog):
        changeDataSourceDialog.setWindowTitle(_translate("changeDataSourceDialog", "undoLayerChanges", None))
        self.label.setText(_translate("changeDataSourceDialog", "URI:", None))
        self.selectDatasourceCombo.setItemText(0, _translate("changeDataSourceDialog", "OGR", None))
        self.selectDatasourceCombo.setItemText(1, _translate("changeDataSourceDialog", "DELIMITED TEXT", None))
        self.selectDatasourceCombo.setItemText(2, _translate("changeDataSourceDialog", "GPX", None))
        self.selectDatasourceCombo.setItemText(3, _translate("changeDataSourceDialog", "POSTGRES", None))
        self.selectDatasourceCombo.setItemText(4, _translate("changeDataSourceDialog", "SPATIALITE", None))
        self.selectDatasourceCombo.setItemText(5, _translate("changeDataSourceDialog", "ORACLE", None))
        self.label_2.setText(_translate("changeDataSourceDialog", "Datasource Types", None))
        self.openBrowser.setText(_translate("changeDataSourceDialog", "....", None))

