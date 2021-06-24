# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/enrico/Dropbox/dev/pickLayer/ui_picksnapdialog.ui'
#
# Created: Wed Apr 27 18:56:48 2016
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_pickSnapDialog(object):
    def setupUi(self, pickSnapDialog):
        pickSnapDialog.setObjectName(_fromUtf8("pickSnapDialog"))
        pickSnapDialog.resize(194, 217)
        self.verticalLayout = QtGui.QVBoxLayout(pickSnapDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(pickSnapDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.snapStateCombo = QtGui.QComboBox(pickSnapDialog)
        self.snapStateCombo.setObjectName(_fromUtf8("snapStateCombo"))
        self.snapStateCombo.addItem(_fromUtf8(""))
        self.snapStateCombo.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.snapStateCombo)
        self.snapModeCombo = QtGui.QComboBox(pickSnapDialog)
        self.snapModeCombo.setObjectName(_fromUtf8("snapModeCombo"))
        self.snapModeCombo.addItem(_fromUtf8(""))
        self.snapModeCombo.addItem(_fromUtf8(""))
        self.snapModeCombo.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.snapModeCombo)
        self.snapUnitsCombo = QtGui.QComboBox(pickSnapDialog)
        self.snapUnitsCombo.setObjectName(_fromUtf8("snapUnitsCombo"))
        self.snapUnitsCombo.addItem(_fromUtf8(""))
        self.snapUnitsCombo.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.snapUnitsCombo)
        self.toleranceCombo = QtGui.QComboBox(pickSnapDialog)
        self.toleranceCombo.setEditable(True)
        self.toleranceCombo.setObjectName(_fromUtf8("toleranceCombo"))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.toleranceCombo.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.toleranceCombo)
        self.avoidIntersections = QtGui.QCheckBox(pickSnapDialog)
        self.avoidIntersections.setObjectName(_fromUtf8("avoidIntersections"))
        self.verticalLayout.addWidget(self.avoidIntersections)
        self.buttonOkNo = QtGui.QDialogButtonBox(pickSnapDialog)
        self.buttonOkNo.setOrientation(QtCore.Qt.Horizontal)
        self.buttonOkNo.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonOkNo.setObjectName(_fromUtf8("buttonOkNo"))
        self.verticalLayout.addWidget(self.buttonOkNo)

        self.retranslateUi(pickSnapDialog)
        QtCore.QMetaObject.connectSlotsByName(pickSnapDialog)

    def retranslateUi(self, pickSnapDialog):
        pickSnapDialog.setWindowTitle(_translate("pickSnapDialog", "Dialog", None))
        self.label.setText(_translate("pickSnapDialog", "TextLabel", None))
        self.snapStateCombo.setItemText(0, _translate("pickSnapDialog", "enabled", None))
        self.snapStateCombo.setItemText(1, _translate("pickSnapDialog", "disabled", None))
        self.snapModeCombo.setItemText(0, _translate("pickSnapDialog", "to vertex", None))
        self.snapModeCombo.setItemText(1, _translate("pickSnapDialog", "to segment", None))
        self.snapModeCombo.setItemText(2, _translate("pickSnapDialog", "to vertex and segment", None))
        self.snapUnitsCombo.setItemText(0, _translate("pickSnapDialog", "map units", None))
        self.snapUnitsCombo.setItemText(1, _translate("pickSnapDialog", "pixels", None))
        self.toleranceCombo.setItemText(0, _translate("pickSnapDialog", "0.00", None))
        self.toleranceCombo.setItemText(1, _translate("pickSnapDialog", "2.50", None))
        self.toleranceCombo.setItemText(2, _translate("pickSnapDialog", "5.00", None))
        self.toleranceCombo.setItemText(3, _translate("pickSnapDialog", "10.0", None))
        self.toleranceCombo.setItemText(4, _translate("pickSnapDialog", "20.0", None))
        self.toleranceCombo.setItemText(5, _translate("pickSnapDialog", "50.0", None))
        self.avoidIntersections.setText(_translate("pickSnapDialog", "Avoid intersections", None))

