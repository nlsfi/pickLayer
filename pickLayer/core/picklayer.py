# -*- coding: utf-8 -*-

#  Copyright (C) 2014-2019 Enrico Ferreguti (enricofer@gmail.com)
#  Copyright (C) 2021-2022 National Land Survey of Finland
#  (https://www.maanmittauslaitos.fi/en).
#
#
#  This file is part of PickLayer.
#
#  PickLayer is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PickLayer is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PickLayer. If not, see <https://www.gnu.org/licenses/>.
import logging
from functools import partial
from time import sleep

from qgis import core
from qgis.gui import QgsRubberBand
from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import QUuid
from qgis.utils import iface, plugins

from pickLayer.core.identifygeometry import IdentifyGeometry
from pickLayer.qgis_plugin_tools.tools.i18n import tr
from pickLayer.qgis_plugin_tools.tools.messages import MsgBar
from pickLayer.qgis_plugin_tools.tools.resources import plugin_name, resources_path

enable_disable = {True: "Enable", False: "Disable"}

LOGGER = logging.getLogger(plugin_name())


class PickLayer:
    """QGIS Plugin Implementation."""

    def __init__(
        self,
    ) -> None:
        """Constructor."""
        # Save reference to the QGIS interface
        self.map_canvas = iface.mapCanvas()
        self.utils = iface.mapCanvas().snappingUtils()
        # initialize plugin directory
        self.cb = QtWidgets.QApplication.clipboard()

        self.map_tool = IdentifyGeometry(self.map_canvas)
        self.map_tool.geom_identified.connect(self.edit_feature)

        self.clip_tool = IdentifyGeometry(self.map_canvas, layerType="VectorLayer")
        self.clip_tool.geom_identified.connect(self.perform_spatial_function)

    def transform_to_current_srs(
        self, p_point: core.QgsPointXY, srs: int
    ) -> core.QgsPointXY:
        # transformation from provided srs to the current SRS
        crc_mappa_corrente = (
            iface.mapCanvas().mapSettings().destinationCrs()
        )  # get current crs
        # print crc_mappa_corrente.srsid()
        crs_dest = crc_mappa_corrente
        crs_src = core.QgsCoordinateReferenceSystem(srs)
        xform = core.QgsCoordinateTransform(
            crs_src, crs_dest, core.QgsProject.instance()
        )
        return xform.transform(p_point)  # forward transformation: src -> dest

    def transform_to_wgs84(self, p_point: core.QgsPointXY, srs: int) -> core.QgsPointXY:
        # transformation from the provided SRS to WGS84
        crs_src = core.QgsCoordinateReferenceSystem(srs)
        crs_dest = core.QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = core.QgsCoordinateTransform(
            crs_src, crs_dest, core.QgsProject.instance()
        )
        return xform.transform(p_point)  # forward transformation: src -> dest

    def populate_attributes_menu(self, attribute_menu: QtWidgets.QMenu) -> None:
        field_names = [field.name() for field in self.selected_layer.fields()]
        for n in range(0, len(field_names)):
            field_name = field_names[n]
            attribute_value = self.selected_feature.attributes()[n]
            try:  # cut long strings
                self.attribute_action = attribute_menu.addAction(
                    "%s: %s" % (field_name, attribute_value[:40])
                )
            except Exception:
                self.attribute_action = attribute_menu.addAction(
                    "%s: %s" % (field_name, attribute_value)
                )
            self.attribute_action.triggered.connect(
                partial(self.copy_to_clipboard, attribute_value)
            )

    def context_menu_request(self) -> None:
        context_menu = QtWidgets.QMenu()
        self.clipboard_layer_action = context_menu.addAction(
            tr("Layer: {}", self.selected_layer.name())
        )
        if self.selected_layer.type() == core.QgsMapLayer.VectorLayer:
            context_menu.addSeparator()
            if self.selected_layer.geometryType() == core.QgsWkbTypes.PointGeometry:
                pp = self.transform_to_current_srs(
                    self.selected_feature.geometry().asPoint(),
                    self.selected_layer.crs(),
                )
                pg = self.transform_to_wgs84(
                    self.selected_feature.geometry().asPoint(),
                    self.selected_layer.crs(),
                )
                self.lon_lat = str(round(pg.x(), 8)) + "," + str(round(pg.y(), 8))
                self.xy = str(round(pp.x(), 8)) + "," + str(round(pp.y(), 8))
                self.clipboard_x_action = context_menu.addAction(
                    "X: " + str(round(pp.x(), 2))
                )
                self.clipboard_y_action = context_menu.addAction(
                    "Y: " + str(round(pp.y(), 2))
                )
                self.clipboard_x_action.triggered.connect(self.clipboard_xy_func)
                self.clipboard_y_action.triggered.connect(self.clipboard_xy_func)
                self.clipboard_lon_action = context_menu.addAction(
                    tr("Lon: {}", str(round(pg.x(), 6)))
                )
                self.clipboard_lat_action = context_menu.addAction(
                    tr("Lat: {}", str(round(pg.y(), 6)))
                )
                self.clipboard_lon_action.triggered.connect(self.clipboard_lon_lat_func)
                self.clipboard_lat_action.triggered.connect(self.clipboard_lon_lat_func)
            elif self.selected_layer.geometryType() == core.QgsWkbTypes.LineGeometry:
                self.leng = round(self.selected_feature.geometry().length(), 2)
                bound = self.selected_feature.geometry().boundingBox()
                self.clipboard_north_action = context_menu.addAction(
                    tr("North: {}", str(round(bound.yMaximum(), 4)))
                )
                self.clipboard_south_action = context_menu.addAction(
                    tr("South: {}", str(round(bound.yMinimum(), 4)))
                )
                self.clipboard_east_action = context_menu.addAction(
                    tr("East: {}", str(round(bound.xMinimum(), 4)))
                )
                self.clipboard_west_action = context_menu.addAction(
                    tr("West: {}", str(round(bound.xMaximum(), 4)))
                )
                self.clipboard_leng_action = context_menu.addAction(
                    tr("Length: {}", str(self.leng))
                )
                self.clipboard_leng_action.triggered.connect(self.clipboard_leng_func)
            elif self.selected_layer.geometryType() == core.QgsWkbTypes.PolygonGeometry:
                self.area = round(self.selected_feature.geometry().area(), 2)
                self.leng = round(self.selected_feature.geometry().length(), 2)
                bound = self.selected_feature.geometry().boundingBox()
                self.clipboard_north_action = context_menu.addAction(
                    tr("North: {}", str(round(bound.yMaximum(), 4)))
                )
                self.clipboard_south_action = context_menu.addAction(
                    tr("South: {}", str(round(bound.yMinimum(), 4)))
                )
                self.clipboard_east_action = context_menu.addAction(
                    tr("East: {}", str(round(bound.xMinimum(), 4)))
                )
                self.clipboard_west_action = context_menu.addAction(
                    tr("West: {}", str(round(bound.xMaximum(), 4)))
                )
                self.clipboard_leng_action = context_menu.addAction(
                    tr("Perimeter: {}", str(self.leng))
                )
                self.clipboard_leng_action.triggered.connect(self.clipboard_leng_func)
                self.clipboard_area_action = context_menu.addAction(
                    tr("Area: {}", str(self.area))
                )
                self.clipboard_area_action.triggered.connect(self.clipboard_area_func)
        context_menu.addSeparator()
        self.set_current_action = context_menu.addAction(
            QtGui.QIcon(resources_path("icons", "mSetCurrentLayer.png")),
            tr("Set current layer"),
        )
        self.hide_action = context_menu.addAction(
            QtGui.QIcon(resources_path("icons", "off.png")),
            tr("Hide"),
        )
        self.open_properties_action = context_menu.addAction(
            QtGui.QIcon(resources_path("icons", "settings.svg")),
            tr("Open properties dialog"),
        )
        self.zoom_to_layer_action = context_menu.addAction(
            QtGui.QIcon(resources_path("icons", "zoomToLayer.png")),
            tr("Zoom to layer extension"),
        )
        self.set_current_action.triggered.connect(self.set_current_func)
        self.hide_action.triggered.connect(self.hide_func)
        self.open_properties_action.triggered.connect(self.open_properties_func)
        self.zoom_to_layer_action.triggered.connect(self.zoom_to_layer_func)
        if self.selected_layer.type() == core.QgsMapLayer.VectorLayer:
            self.open_attribute_table_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "mActionOpenTable.png")),
                tr("Open attribute table"),
            )
            self.open_attribute_table_action.triggered.connect(
                self.open_attribute_table_func
            )
            if self.selected_layer.isEditable():
                self.stop_editing_action = context_menu.addAction(
                    QtGui.QIcon(
                        resources_path(
                            "icons",
                            "mIconEditableEdits.png",
                        )
                    ),
                    tr("Stop editing"),
                )
                self.stop_editing_action.triggered.connect(self.stop_editing_func)
            else:
                self.start_editing_action = context_menu.addAction(
                    QtGui.QIcon(resources_path("icons", "mIconEditable.png")),
                    tr("Start editing"),
                )
                self.start_editing_action.triggered.connect(self.start_editing_func)
            context_menu.addSeparator()
            self.zoom_to_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "zoomToFeature.png")),
                tr("Zoom to feature"),
            )
            self.zoom_to_feature_action.triggered.connect(self.zoom_to_feature_func)
            if self.is_snapping_on(self.selected_layer):
                self.snap_control = (
                    not core.QgsProject.instance()
                    .snappingConfig()
                    .individualLayerSettings(self.selected_layer)
                    .enabled()
                )
                self.snapping_options_action = context_menu.addAction(
                    QtGui.QIcon(resources_path("icons", "snapIcon.png")),
                    enable_disable[self.snap_control] + " snap",
                )
                self.snapping_options_action.triggered.connect(
                    self.snapping_options_func
                )
            if len(QtWidgets.QApplication.clipboard().text().splitlines()) > 1:
                clip_feat_line_txt = (
                    QtWidgets.QApplication.clipboard().text().splitlines()[1]
                )
                clip_feats_txt = clip_feat_line_txt.split("\t")
                self.clip_attrs_fieldnames = (
                    QtWidgets.QApplication.clipboard()
                    .text()
                    .splitlines()[0]
                    .split("\t")[1:]
                )
                self.clip_attrs_values = clip_feats_txt[1:]
                self.clip_geom = core.QgsGeometry.fromWkt(clip_feats_txt[0])
                # if self.clip_geom.isGeosValid():
                if self.selected_layer.isEditable() and self.clip_geom:
                    self.paste_geom_action = context_menu.addAction(
                        QtGui.QIcon(resources_path("icons", "pasteIcon.png")),
                        tr("Paste geometry on feature"),
                    )
                    self.paste_geom_action.triggered.connect(self.paste_geom_func)
                    self.paste_attrs_action = context_menu.addAction(
                        QtGui.QIcon(resources_path("icons", "pasteIcon.png")),
                        tr("Paste attributes on feature"),
                    )
                    self.paste_attrs_action.triggered.connect(self.paste_attrs_func)
            self.clip_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "subtractIcon.png")),
                tr("Select feature and Subtract"),
            )
            self.clip_feature_action.triggered.connect(self.clip_feature_func)
            self.clip_feature_action.setEnabled(self.selected_layer.isEditable())
            self.merge_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "mergeIcon.png")),
                tr("Select feature and Merge"),
            )
            self.merge_feature_action.triggered.connect(self.merge_feature_func)
            self.merge_feature_action.setEnabled(self.selected_layer.isEditable())
            self.make_valid_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "makeValidIcon.png")),
                tr("Make Valid Geometry"),
            )
            self.make_valid_feature_action.triggered.connect(
                self.make_valid_feature_func
            )
            self.make_valid_feature_action.setEnabled(self.selected_layer.isEditable())
            self.copy_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "copyIcon.png")),
                tr("Copy feature"),
            )
            self.copy_feature_action.triggered.connect(self.copy_feature_func)
            self.attribute_menu = context_menu.addMenu(
                QtGui.QIcon(resources_path("icons", "viewAttributes.png")),
                tr("Feature attributes view"),
            )
            self.populate_attributes_menu(self.attribute_menu)
            self.edit_feature_action = context_menu.addAction(
                QtGui.QIcon(resources_path("icons", "mActionPropertyItem.png")),
                tr("Feature attributes edit"),
            )
            self.edit_feature_action.triggered.connect(self.edit_feature_func)
            if self.selected_layer.actions().actions():
                action_order = 0
                context_menu.addSeparator()
                for action in self.selected_layer.actions().actions():
                    custom_icon = (
                        action.icon()
                        if action.icon().name()
                        else QtGui.QIcon(resources_path("icons", "customAction.png"))
                    )

                    new_action_item = context_menu.addAction(custom_icon, action.name())
                    new_action_item.triggered.connect(
                        partial(self.custom_action, action.id())
                    )
                    action_order += 1
        context_menu.exec_(QtGui.QCursor.pos())

    def zoom_to_feature_func(self) -> None:
        feature_box = self.selected_feature.geometry().boundingBox()
        p1 = self.transform_to_current_srs(
            core.QgsPointXY(feature_box.xMinimum(), feature_box.yMinimum()),
            self.selected_layer.crs(),
        )
        p2 = self.transform_to_current_srs(
            core.QgsPointXY(feature_box.xMaximum(), feature_box.yMaximum()),
            self.selected_layer.crs(),
        )
        self.map_canvas.setExtent(core.QgsRectangle(p1.x(), p1.y(), p2.x(), p2.y()))
        self.map_canvas.refresh()

    def zoom_to_layer_func(self) -> None:
        layer_box = self.selected_layer.extent()
        p1 = self.transform_to_current_srs(
            core.QgsPointXY(layer_box.xMinimum(), layer_box.yMinimum()),
            self.selected_layer.crs(),
        )
        p2 = self.transform_to_current_srs(
            core.QgsPointXY(layer_box.xMaximum(), layer_box.yMaximum()),
            self.selected_layer.crs(),
        )
        self.map_canvas.setExtent(core.QgsRectangle(p1.x(), p1.y(), p2.x(), p2.y()))
        self.map_canvas.refresh()

    def set_current_func(self) -> None:
        iface.setActiveLayer(self.selected_layer)

    def custom_action(self, action_id: QUuid) -> None:
        self.selected_layer.actions().doActionFeature(action_id, self.selected_feature)

    def hide_func(self) -> None:
        core.QgsProject.instance().layerTreeRoot().findLayer(
            self.selected_layer.id()
        ).setItemVisibilityChecked(False)

    def open_properties_func(self) -> None:
        iface.showLayerProperties(self.selected_layer)

    def open_attribute_table_func(self) -> None:
        iface.showAttributeTable(self.selected_layer)

    def copy_to_clipboard(self, copy_value: str) -> None:
        self.cb.setText(copy_value)

    def clipboard_xy_func(self) -> None:
        self.cb.setText(self.xy)

    def clipboard_lon_lat_func(self) -> None:
        self.cb.setText(self.lon_lat)

    def clipboard_leng_func(self) -> None:
        self.cb.setText(str(self.leng))

    def clipboard_area_func(self) -> None:
        self.cb.setText(str(self.area))

    def stop_editing_func(self) -> None:
        iface.setActiveLayer(self.selected_layer)
        iface.actionToggleEditing().trigger()

    def start_editing_func(self) -> None:
        iface.setActiveLayer(self.selected_layer)
        iface.actionToggleEditing().trigger()

    def is_snapping_on(self, layer: core.QgsMapLayer) -> bool:
        global_snapping_config = core.QgsProject.instance().snappingConfig()
        return (
            global_snapping_config.enabled()
            and global_snapping_config.mode()
            == core.QgsSnappingConfig.AdvancedConfiguration
        )

    def snapping_options_func(self) -> None:
        global_snapping_config = core.QgsProject.instance().snappingConfig()
        layer_snap_config = global_snapping_config.individualLayerSettings(
            self.selected_layer
        )
        layer_snap_config.setEnabled(self.snap_control)
        global_snapping_config.setIndividualLayerSettings(
            self.selected_layer, layer_snap_config
        )
        core.QgsProject.instance().setSnappingConfig(global_snapping_config)

    def edit_feature_func(self) -> None:
        iface.openFeatureForm(self.selected_layer, self.selected_feature, True)

    def copy_feature_func(self) -> None:
        bak_active_layer = iface.activeLayer()
        iface.setActiveLayer(self.selected_layer)
        self.selected_layer.selectByIds([self.selected_feature.id()])
        if "attributePainter" in plugins:
            ap = plugins["attributePainter"]
            ap.setSourceFeature(self.selected_layer, self.selected_feature)
            self.map_canvas.setMapTool(self.map_tool)
            ap.apdockwidget.show()
        iface.actionCopyFeatures().trigger()
        iface.setActiveLayer(bak_active_layer)

    def paste_geom_func(self) -> None:
        self.selected_layer.changeGeometry(self.selected_feature.id(), self.clip_geom)
        self.selected_layer.updateExtents()
        self.selected_layer.setCacheImage(None)
        self.selected_layer.triggerRepaint()

    def paste_attrs_func(self) -> None:
        for attr_id in range(0, len(self.clip_attrs_values)):
            if self.selected_layer.pendingFields().field(
                str(self.clip_attrs_fieldnames[attr_id])
            ):
                self.selected_layer.changeAttributeValue(
                    self.selected_feature.id(), attr_id, self.clip_attrs_values[attr_id]
                )

    def edit_feature(self, layer: core.QgsMapLayer, feature: core.QgsFeature) -> None:
        self.selected_layer = layer
        self.selected_feature = feature
        self.highlight(feature.geometry())
        self.context_menu_request()

    def set_map_tool(self) -> None:
        self.map_canvas.setMapTool(self.map_tool)

    def highlight(self, geometry: core.QgsGeometry) -> None:
        def process_events() -> None:
            try:
                QtGui.qApp.processEvents()
            except Exception:
                QtWidgets.QApplication.processEvents()

        highlight = QgsRubberBand(iface.mapCanvas(), geometry.type())
        highlight.setColor(QtGui.QColor("#36AF6C"))
        highlight.setFillColor(QtGui.QColor("#36AF6C"))
        highlight.setWidth(2)
        highlight.setToGeometry(geometry, self.selected_layer)
        process_events()
        sleep(0.1)
        highlight.hide()
        process_events()
        sleep(0.1)
        highlight.show()
        process_events()
        sleep(0.1)
        highlight.reset()
        process_events()

    def clip_feature_func(self) -> None:
        self.spatial_function = self.selected_feature.geometry().difference
        self.spatial_predicate = "clipped"
        self.map_canvas.setMapTool(self.clip_tool)

    def merge_feature_func(self) -> None:
        self.spatial_function = self.selected_feature.geometry().combine
        self.spatial_predicate = "merged"
        self.map_canvas.setMapTool(self.clip_tool)

    def make_valid_feature_func(self) -> None:
        valid_geometry = self.selected_feature.geometry().makeValid()
        self.selected_feature.setGeometry(valid_geometry)
        self.selected_layer.updateFeature(self.selected_feature)
        self.selected_layer.triggerRepaint()
        self.highlight(self.selected_feature.geometry())

    def perform_spatial_function(
        self, clip_layer: core.QgsVectorLayer, clip_feature: core.QgsFeature
    ) -> None:
        if clip_feature.geometry().type() != self.selected_feature.geometry().type():
            MsgBar.warning(
                tr("Can't perform spatial function on different geometry types")
            )
        else:
            clipped_geometry = self.spatial_function(clip_feature.geometry())
            if clipped_geometry:
                self.selected_feature.setGeometry(clipped_geometry)
                self.selected_layer.updateFeature(self.selected_feature)
                if clip_layer == self.selected_layer:
                    self.selected_layer.deleteFeature(clip_feature.id())
                self.selected_layer.triggerRepaint()
                MsgBar.info(
                    tr(
                        "Source Geometry succesfully clipped: {}",
                        self.spatial_predicate,
                    ),
                    success=True,
                )
                self.highlight(clipped_geometry)
            else:
                MsgBar.warning(tr("Invalid processed geometry"))

        self.map_canvas.setMapTool(self.map_tool)
