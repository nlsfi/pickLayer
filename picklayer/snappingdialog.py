# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pickLayerSnappingDialog
                                 A QGIS plugin
 pick layer
                             -------------------
        begin                : 2014-06-16
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Enrico Ferreguti
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


from PyQt4 import QtCore, QtGui, uic
from qgis.core import *
from ui_picksnapdialog import Ui_pickSnapDialog


class trace:

    def __init__(self):
        self.trace = None
        
    def ce(self,string):
        if self.trace:
            print string

class snappingDialog(QtGui.QDialog, Ui_pickSnapDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.mapCanvas = iface.mapCanvas()
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.tra = trace()
        self.buttonOkNo.accepted.connect(self.saveSnappingOptions)
        self.buttonOkNo.rejected.connect(self.cancelSnappingOptions)

    def cancelSnappingOptions(self):
        self.hide()

    def saveSnappingOptions(self):
        # hide the dialog
        self.hide()
        if self.snapStateCombo.currentIndex() == 0:
            enabled = True
        else:
            enabled = False
        snappingType = self.snapModeCombo.currentIndex()
        if self.snapModeCombo.currentIndex() == 1:
            unitType = 1
        else:
            unitType = 0
        tolerance = float(self.toleranceCombo.currentText())
        avoidInterceptions = self.avoidIntersections.isChecked()
        '''
        utils = self.mapCanvas.snappingUtils()
        if utils.SnapToMapMode() != QgsSnappingUtils.SnapAdvanced:
            root = QgsProject.instance().layerTreeRoot()
            layer_list = []
            for layer in root.findLayers():
                # LayerConfig(layer, snapping type, tolerance, units)
                if layer.layer().type() == QgsMapLayer.VectorLayer:
                    layer_list.append(utils.LayerConfig(layer.layer(), QgsPointLocator.Vertex, 5.0, 2))
            utils.setLayers(layer_list)
            utils.setSnapToMapMode(QgsSnappingUtils.SnapAdvanced)
            self.mapCanvas.setSnappingUtils(utils)
        '''
        proj = QgsProject.instance()
        print self.selectedLayer.id(),enabled,snappingType,unitType,tolerance,avoidInterceptions
        proj.setSnapSettingsForLayer(self.selectedLayer.id(),enabled,snappingType,unitType,tolerance,avoidInterceptions)
        

    def getSnappingOptionsDialog(self,layer):
        self.selectedLayer = layer
        proj = QgsProject.instance()
        res = proj.snapSettingsForLayer(layer.id())
        self.compileSnapForm(res)
        self.label.setText(self.selectedLayer.name())
        self.show()

    def compileSnapForm(self,snappingOptions):
        print snappingOptions
        enabled = snappingOptions[1]
        snappingType = snappingOptions[2]
        unitType = snappingOptions[3]
        tolerance = snappingOptions[4]
        avoidInterceptions = snappingOptions[5]
        if enabled:
            self.snapStateCombo.setCurrentIndex(0)
        else:
            self.snapStateCombo.setCurrentIndex(1)
        self.snapModeCombo.setCurrentIndex(snappingType)
        if unitType == 1:
            self.snapModeCombo.setCurrentIndex(1)
        else:
            self.snapModeCombo.setCurrentIndex(0)
        self.toleranceCombo.insertItem(0,str(tolerance))
        self.toleranceCombo.setCurrentIndex(0)
        if avoidInterceptions:
            self.avoidIntersections.setCheckState(True)
        else:
            self.avoidIntersections.setChecked(False)
        self.avoidIntersections.setChecked(avoidInterceptions)
