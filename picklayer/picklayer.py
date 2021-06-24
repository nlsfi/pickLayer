# -*- coding: utf-8 -*-
"""
/***************************************************************************
 autoSaver
                                 A QGIS plugin
 auto save current project
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
from PyQt5 import Qt, QtCore, QtWidgets, QtGui, QtWebKit, QtWebKitWidgets, QtXml, QtNetwork, uic
from qgis import core, utils, gui

from qgis.utils import plugins
from qgis.core import Qgis
from qgis.gui import QgsAttributeDialog, QgsMessageBar, QgsRubberBand
from functools import *

from .identifygeometry import IdentifyGeometry
import os.path
from time import sleep

def stringToPythonNames(string):
    validPyChars="1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_"
    stringOK=""
    for char in string.encode('ascii', 'ignore'):
        if char in validPyChars:
            stringOK += char
    return "action_"+stringOK

enable_disable = {
    True: "Enable",
    False: "Disable"
}

class pickLayer:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.utils = iface.mapCanvas().snappingUtils()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        #self.snapDlg = snappingDialog(iface)
        #self.tra = trace()
        self.cb = QtWidgets.QApplication.clipboard()


    def transformToCurrentSRS(self, pPoint, srs):
        # transformation from provided srs to the current SRS
        crcMappaCorrente = self.iface.mapCanvas().mapSettings().destinationCrs() # get current crs
        #print crcMappaCorrente.srsid()
        crsDest = crcMappaCorrente
        crsSrc = core.QgsCoordinateReferenceSystem(srs)
        xform = core.QgsCoordinateTransform(crsSrc, crsDest, core.QgsProject.instance())
        return xform.transform(pPoint) # forward transformation: src -> dest

    def transformToWGS84(self, pPoint, srs):
        # transformation from the provided SRS to WGS84
        crsSrc = core.QgsCoordinateReferenceSystem(srs)
        crsDest = core.QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = core.QgsCoordinateTransform(crsSrc, crsDest, core.QgsProject.instance())
        return xform.transform(pPoint) # forward transformation: src -> dest

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        #icon_path = ':/plugins/pickLayer/icon.png'
        icon_path = os.path.join(self.plugin_dir, "icons", "pickLayer.png")
        # map tool action
        self.mapToolAction = QtWidgets.QAction(QtGui.QIcon(icon_path),"Pick to Layer", self.iface.mainWindow())
        self.mapToolAction.setCheckable(True)
        self.mapTool = IdentifyGeometry(self.mapCanvas)
        self.mapTool.geomIdentified.connect(self.editFeature)
        self.mapTool.setAction(self.mapToolAction)

        self.clipTool = IdentifyGeometry(self.mapCanvas,layerType = 'VectorLayer')
        self.clipTool.geomIdentified.connect(self.performSpatialFunction)

        self.mapToolAction.triggered.connect(self.setMapTool)
        self.iface.addToolBarIcon(self.mapToolAction)
        self.iface.addPluginToMenu("&Pick to Layer", self.mapToolAction)

    def populateAttributesMenu(self,attributeMenu):
        field_names = [field.name() for field in self.selectedLayer.fields()]
        for n in range(0,len(field_names)):
            fieldName = field_names[n]
            attributeValue = self.selectedFeature.attributes()[n]
            try:#cut long strings
                self.attributeAction = attributeMenu.addAction("%s: %s" % (fieldName,attributeValue[:40]))
            except:
                self.attributeAction = attributeMenu.addAction("%s: %s" % (fieldName,attributeValue))
            self.attributeAction.triggered.connect(partial(self.copyToClipboard,attributeValue))

    def contextMenuRequest(self):
        contextMenu = QtWidgets.QMenu()
        self.clipboardLayerAction = contextMenu.addAction("Layer: "+self.selectedLayer.name())
        if self.selectedLayer.type() == core.QgsMapLayer.VectorLayer:
            contextMenu.addSeparator()
            if self.selectedLayer.geometryType() == core.QgsWkbTypes.PointGeometry :
                pp = self.transformToCurrentSRS(self.selectedFeature.geometry().asPoint(),self.selectedLayer.crs())
                pg = self.transformToWGS84(self.selectedFeature.geometry().asPoint(),self.selectedLayer.crs())
                self.lonLat = str(round(pg.x(),8))+","+str(round(pg.y(),8))
                self.xy = str(round(pp.x(),8))+","+str(round(pp.y(),8))
                self.clipboardXAction = contextMenu.addAction("X: "+str(round(pp.x(),2)))
                self.clipboardYAction = contextMenu.addAction("Y: "+str(round(pp.y(),2)))
                self.clipboardXAction.triggered.connect(self.clipboardXYFunc)
                self.clipboardYAction.triggered.connect(self.clipboardXYFunc)
                self.clipboardLonAction = contextMenu.addAction("Lon: "+str(round(pg.x(),6)))
                self.clipboardLatAction = contextMenu.addAction("Lat: "+str(round(pg.y(),6)))
                self.clipboardLonAction.triggered.connect(self.clipboardLonLatFunc)
                self.clipboardLatAction.triggered.connect(self.clipboardLonLatFunc)
            elif self.selectedLayer.geometryType() == core.QgsWkbTypes.LineGeometry:
                self.leng = round (self.selectedFeature.geometry().length(),2)
                bound = self.selectedFeature.geometry().boundingBox()
                self.clipboardNorthAction = contextMenu.addAction("North: "+str(round(bound.yMaximum(),4)))
                self.clipboardSouthAction = contextMenu.addAction("South: "+str(round(bound.yMinimum(),4)))
                self.clipboardEastAction = contextMenu.addAction("East: "+str(round(bound.xMinimum(),4)))
                self.clipboardWestAction = contextMenu.addAction("West: "+str(round(bound.xMaximum(),4)))
                self.clipboardLengAction = contextMenu.addAction("Length: "+str(self.leng))
                self.clipboardLengAction.triggered.connect(self.clipboardLengFunc)
            elif self.selectedLayer.geometryType() == core.QgsWkbTypes.PolygonGeometry:
                self.area = round (self.selectedFeature.geometry().area(),2)
                self.leng = round (self.selectedFeature.geometry().length(),2)
                bound = self.selectedFeature.geometry().boundingBox()
                self.clipboardNorthAction = contextMenu.addAction("North: "+str(round(bound.yMaximum(),4)))
                self.clipboardSouthAction = contextMenu.addAction("South: "+str(round(bound.yMinimum(),4)))
                self.clipboardEastAction = contextMenu.addAction("East: "+str(round(bound.xMinimum(),4)))
                self.clipboardWestAction = contextMenu.addAction("West: "+str(round(bound.xMaximum(),4)))
                self.clipboardLengAction = contextMenu.addAction("Perimeter: "+str(self.leng))
                self.clipboardLengAction.triggered.connect(self.clipboardLengFunc)
                self.clipboardAreaAction = contextMenu.addAction("Area: "+str(self.area))
                self.clipboardAreaAction.triggered.connect(self.clipboardAreaFunc)
        contextMenu.addSeparator()
        self.setCurrentAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mSetCurrentLayer.png")), "Set current layer")
        self.hideAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "off.png")), "Hide")
        self.openPropertiesAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "settings.svg")), "Open properties dialog")
        self.zoomToLayerAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "zoomToLayer.png")), "Zoom to layer extension")
        self.setCurrentAction.triggered.connect(self.setCurrentFunc)
        self.hideAction.triggered.connect(self.hideFunc)
        self.openPropertiesAction.triggered.connect(self.openPropertiesFunc)
        self.zoomToLayerAction.triggered.connect(self.zoomToLayerFunc)
        if self.selectedLayer.type() == core.QgsMapLayer.VectorLayer:
            self.openAttributeTableAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mActionOpenTable.png")), "Open attribute table")
            self.openAttributeTableAction.triggered.connect(self.openAttributeTableFunc)
            if self.selectedLayer.isEditable():
                self.stopEditingAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mIconEditableEdits.png")), "Stop editing")
                self.stopEditingAction.triggered.connect(self.stopEditingFunc)
            else:
                self.startEditingAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mIconEditable.png")), "Start editing")
                self.startEditingAction.triggered.connect(self.startEditingFunc)
            contextMenu.addSeparator()
            self.zoomToFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "zoomToFeature.png")), "Zoom to feature")
            self.zoomToFeatureAction.triggered.connect(self.zoomToFeatureFunc)
            if self.isSnappingOn(self.selectedLayer):
                self.snap_control = not core.QgsProject.instance().snappingConfig().individualLayerSettings(self.selectedLayer).enabled()
                self.snappingOptionsAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "snapIcon.png")), enable_disable[self.snap_control] + " snap")
                self.snappingOptionsAction.triggered.connect(self.snappingOptionsFunc)
            if len(QtWidgets.QApplication.clipboard().text().splitlines()) > 1:
                clipFeatLineTXT = QtWidgets.QApplication.clipboard().text().splitlines()[1]
                clipFeatsTXT = clipFeatLineTXT.split('\t')
                self.clipAttrsFieldnames = QtWidgets.QApplication.clipboard().text().splitlines()[0].split('\t')[1:]
                self.clipAttrsValues = clipFeatsTXT[1:]
                self.clipGeom = core.QgsGeometry.fromWkt(clipFeatsTXT[0])
                #if self.clipGeom.isGeosValid():
                if self.selectedLayer.isEditable() and self.clipGeom:
                    self.pasteGeomAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "pasteIcon.png")), "Paste geometry on feature")
                    self.pasteGeomAction.triggered.connect(self.pasteGeomFunc)
                    self.pasteAttrsAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "pasteIcon.png")), "Paste attributes on feature")
                    self.pasteAttrsAction.triggered.connect(self.pasteAttrsFunc)
            self.clipFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "subtractIcon.png")), "Select feature and Subtract")
            self.clipFeatureAction.triggered.connect(self.clipFeatureFunc)
            self.clipFeatureAction.setEnabled(self.selectedLayer.isEditable())
            self.mergeFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mergeIcon.png")), "Select feature and Merge")
            self.mergeFeatureAction.triggered.connect(self.mergeFeatureFunc)
            self.mergeFeatureAction.setEnabled(self.selectedLayer.isEditable())
            self.makeValidFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "makeValidIcon.png")), "Make Valid Geometry")
            self.makeValidFeatureAction.triggered.connect(self.makeValidFeatureFunc)
            self.makeValidFeatureAction.setEnabled(self.selectedLayer.isEditable())
            self.copyFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "copyIcon.png")), "Copy feature")
            self.copyFeatureAction.triggered.connect(self.copyFeatureFunc)
            self.attributeMenu = contextMenu.addMenu(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "viewAttributes.png")), "Feature attributes view")
            self.populateAttributesMenu(self.attributeMenu)
            self.editFeatureAction = contextMenu.addAction(QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "mActionPropertyItem.png")), "Feature attributes edit")
            self.editFeatureAction.triggered.connect(self.editFeatureFunc)
            if self.selectedLayer.actions().actions():
                actionOrder = 0
                contextMenu.addSeparator()
                for action in self.selectedLayer.actions().actions():
                    try:
                        customIcon = action.icon()
                    except:
                        customIcon = QtGui.QIcon(os.path.join(self.plugin_dir, "icons", "customAction.png"))
                    newActionItem = contextMenu.addAction(customIcon,action.name())
                    newActionItem.triggered.connect(partial(self.customAction,actionOrder))
                    actionOrder += 1
        contextMenu.exec_(QtGui.QCursor.pos())

    def zoomToFeatureFunc(self):
        featureBox = self.selectedFeature.geometry().boundingBox()
        p1 = self.transformToCurrentSRS(core.QgsPointXY(featureBox.xMinimum(),featureBox.yMinimum()),self.selectedLayer.crs())
        p2 = self.transformToCurrentSRS(core.QgsPointXY(featureBox.xMaximum(),featureBox.yMaximum()),self.selectedLayer.crs())
        self.mapCanvas.setExtent(core.QgsRectangle(p1.x(),p1.y(),p2.x(),p2.y()))
        self.mapCanvas.refresh()

    def zoomToLayerFunc(self):
        layerBox = self.selectedLayer.extent()
        p1 = self.transformToCurrentSRS(core.QgsPointXY(layerBox.xMinimum(),layerBox.yMinimum()),self.selectedLayer.crs())
        p2 = self.transformToCurrentSRS(core.QgsPointXY(layerBox.xMaximum(),layerBox.yMaximum()),self.selectedLayer.crs())
        self.mapCanvas.setExtent(core.QgsRectangle(p1.x(),p1.y(),p2.x(),p2.y()))
        self.mapCanvas.refresh()

    def setCurrentFunc(self):
        self.iface.setActiveLayer(self.selectedLayer)

    def customAction(self,actionId):
        self.selectedLayer.actions().doActionFeature(actionId,self.selectedFeature)

    def hideFunc(self):
        core.QgsProject.instance().layerTreeRoot().findLayer(self.selectedLayer.id()).setItemVisibilityChecked(False)

    def openPropertiesFunc(self):
        self.iface.showLayerProperties(self.selectedLayer)

    def openAttributeTableFunc(self):
        self.iface.showAttributeTable(self.selectedLayer)

    def copyToClipboard(self,copyValue):
        self.cb.setText(copyValue)

    def clipboardXYFunc(self):
        self.cb.setText(self.xy)

    def clipboardLonLatFunc(self):
        self.cb.setText(self.lonLat)

    def clipboardLengFunc(self):
        self.cb.setText(str(self.leng))

    def clipboardAreaFunc(self):
        self.cb.setText(str(self.area))

    def stopEditingFunc(self):
        self.iface.setActiveLayer(self.selectedLayer)
        self.iface.actionToggleEditing().trigger()

    def startEditingFunc(self):
        self.iface.setActiveLayer(self.selectedLayer)
        self.iface.actionToggleEditing().trigger()


    def isSnappingOn(self,layer):
        globalSnappingConfig = core.QgsProject.instance().snappingConfig()
        return globalSnappingConfig.enabled() and globalSnappingConfig.mode() == core.QgsSnappingConfig.AdvancedConfiguration

    def snappingOptionsFunc(self):
        globalSnappingConfig = core.QgsProject.instance().snappingConfig()
        layerSnapConfig = globalSnappingConfig.individualLayerSettings(self.selectedLayer)
        layerSnapConfig.setEnabled(self.snap_control)
        globalSnappingConfig.setIndividualLayerSettings(self.selectedLayer, layerSnapConfig)
        core.QgsProject.instance().setSnappingConfig(globalSnappingConfig)

    def editFeatureFunc(self):
        self.iface.openFeatureForm(self.selectedLayer,self.selectedFeature,True)

    def copyFeatureFunc(self):
        bakActiveLayer = self.iface.activeLayer()
        self.iface.setActiveLayer(self.selectedLayer)
        self.selectedLayer.setSelectedFeatures([self.selectedFeature.id()])
        if 'attributePainter' in plugins:
            ap = plugins['attributePainter']
            ap.setSourceFeature(self.selectedLayer, self.selectedFeature)
            self.mapCanvas.setMapTool(self.mapTool)
            ap.apdockwidget.show()
        self.iface.actionCopyFeatures().trigger()
        self.iface.setActiveLayer(bakActiveLayer)


    def pasteGeomFunc(self):
        self.selectedLayer.changeGeometry(self.selectedFeature.id(), self.clipGeom)
        self.selectedLayer.updateExtents()
        self.selectedLayer.setCacheImage(None)
        self.selectedLayer.triggerRepaint()

    def pasteAttrsFunc(self):
        for attrId in range(0,len(self.clipAttrsValues)):
            if self.selectedLayer.pendingFields().field(str(self.clipAttrsFieldnames[attrId])):
                self.selectedLayer.changeAttributeValue(self.selectedFeature.id(),attrId,self.clipAttrsValues[attrId])

    def editFeature(self,layer,feature):
        self.selectedLayer = layer
        self.selectedFeature = feature
        self.highlight(feature.geometry())
        self.contextMenuRequest()
        pass

    def unload(self):
        self.iface.removePluginMenu("&Pick to Layer", self.mapToolAction)
        self.iface.removeToolBarIcon(self.mapToolAction)

    def setMapTool(self):
        self.mapCanvas.setMapTool(self.mapTool)

    def highlight(self,geometry):
        def processEvents():
            try:
                QtGui.qApp.processEvents()
            except:
                QtWidgets.QApplication.processEvents()

        highlight = QgsRubberBand(self.iface.mapCanvas(), geometry.type())
        highlight.setColor(QtGui.QColor("#36AF6C"))
        highlight.setFillColor(QtGui.QColor("#36AF6C"))
        highlight.setWidth(2)
        highlight.setToGeometry(geometry,self.iface.mapCanvas().currentLayer())
        processEvents()
        sleep(.1)
        highlight.hide()
        processEvents()
        sleep(.1)
        highlight.show()
        processEvents()
        sleep(.1)
        highlight.reset()
        processEvents()

    def clipFeatureFunc(self):
        self.spatialFunction = self.selectedFeature.geometry().difference
        self.spatialPredicate = "clipped"
        self.mapCanvas.setMapTool(self.clipTool)

    def mergeFeatureFunc(self):
        self.spatialFunction = self.selectedFeature.geometry().combine
        self.spatialPredicate = "merged"
        self.mapCanvas.setMapTool(self.clipTool)

    def makeValidFeatureFunc(self):
        validGeometry = self.selectedFeature.geometry().makeValid()
        self.selectedFeature.setGeometry(validGeometry)
        self.selectedLayer.updateFeature(self.selectedFeature)
        self.selectedLayer.triggerRepaint()
        self.highlight(self.selectedFeature.geometry())

    def performSpatialFunction(self,clipLayer,clipFeature):
        if clipFeature.geometry().type() != self.selectedFeature.geometry().type():
            self.iface.messageBar().pushMessage("PickLayer plugin", "Can't perform spatial function on different geometry types" , level=Qgis.Warning, duration=4)
        else:
            clippedGeometry = self.spatialFunction(clipFeature.geometry())
            if clippedGeometry:
                self.selectedFeature.setGeometry(clippedGeometry)
                self.selectedLayer.updateFeature(self.selectedFeature)
                if clipLayer == self.selectedLayer:
                    self.selectedLayer.deleteFeature(clipFeature.id())
                self.selectedLayer.triggerRepaint()
                self.iface.messageBar().pushMessage("PickLayer plugin", "Source Geometry succesfully " + self.spatialPredicate , level=Qgis.Success, duration=4)
                self.highlight(clippedGeometry)
            else:
                self.iface.messageBar().pushMessage("PickLayer plugin", "Invalid processed geometry" , level=Qgis.Warning, duration=4)
        self.mapCanvas.setMapTool(self.mapTool)
