# -*- coding: utf-8 -*-

#  Copyright (C) 2022 National Land Survey of Finland
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
from typing import List, Optional

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsMapLayer,
    QgsPointXY,
    QgsProject,
    QgsRenderContext,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapTool, QgsMapToolIdentify
from qgis.PyQt.QtCore import QPoint
from qgis.PyQt.QtGui import QCursor
from qgis.utils import iface
from qgis_plugin_tools.tools.i18n import tr
from qgis_plugin_tools.tools.messages import MsgBar
from qgis_plugin_tools.tools.resources import plugin_name

from pickLayer.definitions.settings import Settings

LOGGER = logging.getLogger(plugin_name())


class SetActiveLayerTool(QgsMapToolIdentify):
    """
    Map tool that sets active layer by a click on the map canvas.

    New active layer is determined based on the feature that is closest
    to the clicked coordinate. If the identify query finds features
    from multiple layers the active layer is selected from the first
    identify result. Identify results are in same order as
    the search_layer_ids parameter. If search_layer_ids is empty then the
    result list is in same order as iface.mapCanvas().layers().

    Map tool is automatically deactived and swapped to previous map tool
    after the new active layer is set.
    """

    def __init__(
        self,
        canvas: QgsMapCanvas,
    ) -> None:
        super().__init__(canvas)
        self.setCursor(QCursor())
        self.previous_map_tool: Optional[QgsMapTool] = None
        self.search_layer_ids: Optional[List[str]] = None

    def canvasReleaseEvent(self, mouse_event: QgsMapMouseEvent) -> None:  # noqa N802
        try:
            self.set_active_layer_using_closest_feature(
                self.toMapCoordinates(QPoint(mouse_event.x(), mouse_event.y()))
            )
        except Exception as e:
            MsgBar.exception(
                tr("Error occurred: {}", str(e)), tr("Check log for more details.")
            )

    def set_active_layer_using_closest_feature(
        self,
        location: QgsPointXY,
        search_radius: Optional[float] = None,
        search_layer_ids: Optional[List[str]] = None,
    ) -> None:

        if search_radius is None:
            search_radius = self._get_default_search_radius()

        self.setCanvasPropertiesOverrides(search_radius)

        results = self._get_identify_results(location, search_layer_ids)

        self.restoreCanvasPropertiesOverrides()

        layer_to_activate = self._choose_layer_from_identify_results(results, location)

        if layer_to_activate is not None:
            LOGGER.info(tr("Activating layer {}", layer_to_activate.name()))
            self._activate_layer_and_previous_map_tool(layer_to_activate)

    def _get_identify_results(
        self, location: QgsPointXY, search_layer_ids: Optional[List[str]] = None
    ) -> List[QgsMapToolIdentify.IdentifyResult]:
        layers = []
        if search_layer_ids:
            for layer_id in search_layer_ids:
                layer = QgsProject.instance().mapLayer(layer_id)
                if isinstance(layer, QgsVectorLayer):
                    layers.append(layer)

        if len(layers) > 0:
            return self.identify(
                geometry=QgsGeometry.fromPointXY(location),
                mode=QgsMapToolIdentify.TopDownAll,
                layerList=layers,
                layerType=QgsMapToolIdentify.VectorLayer,
            )
        return self.identify(
            geometry=QgsGeometry.fromPointXY(location),
            mode=QgsMapToolIdentify.TopDownAll,
            layerType=QgsMapToolIdentify.VectorLayer,
        )

    def _activate_layer_and_previous_map_tool(
        self, layer_to_activate: QgsMapLayer
    ) -> None:
        iface.setActiveLayer(layer_to_activate)
        if self.previous_map_tool is None:
            LOGGER.info(
                tr("Previous map tool not found: Set Active Layer tool remains active.")
            )
            return
        iface.mapCanvas().setMapTool(self.previous_map_tool)

    def _get_default_search_radius(self) -> float:
        # For some reason overriding searchRadiusMM does not seem to affect
        # searchRadiusMU. Logic copied here from QgsMapTool.searchRadiusMU
        context = QgsRenderContext.fromMapSettings(self.canvas().mapSettings())
        return (
            float(Settings.search_radius.get())
            * context.scaleFactor()
            * context.mapToPixel().mapUnitsPerPixel()
        )

    def _get_distance_to_feature_on_layer(
        self,
        layer: QgsVectorLayer,
        feature: QgsFeature,
        origin_map_point: QgsPointXY,
    ) -> float:
        # for unknown reasons saving all geoms to variables avoids fatal exs
        origin_layer_point = self.toLayerCoordinates(layer, origin_map_point)
        origin_geom = QgsGeometry.fromPointXY(origin_layer_point)
        feature_geom = feature.geometry()
        closest_geom = feature_geom.nearestPoint(origin_geom)
        closest_layer_point = closest_geom.asPoint()
        closest_map_point = self.toMapCoordinates(layer, closest_layer_point)
        return origin_map_point.distance(closest_map_point)

    def _choose_layer_from_identify_results(
        self,
        results: List[QgsMapToolIdentify.IdentifyResult],
        origin_map_coordinates: QgsPointXY,
    ) -> Optional[QgsMapLayer]:

        geom_type_preference = {
            QgsWkbTypes.PointGeometry: 1,
            QgsWkbTypes.LineGeometry: 2,
            QgsWkbTypes.PolygonGeometry: 3,
        }

        best_match: Optional[QgsVectorLayer] = None
        best_match_geom_type_preference = 0
        best_match_distance = 0.0

        for result in results:
            if not isinstance(result.mLayer, QgsVectorLayer):
                continue

            if (
                best_match is None
                or geom_type_preference.get(result.mLayer.geometryType(), 99)
                < best_match_geom_type_preference
                or (
                    geom_type_preference.get(result.mLayer.geometryType(), 99)
                    == best_match_geom_type_preference
                    and self._get_distance_to_feature_on_layer(
                        result.mLayer, result.mFeature, origin_map_coordinates
                    )
                    < best_match_distance
                )
            ):
                best_match = result.mLayer
                best_match_geom_type_preference = geom_type_preference.get(
                    result.mLayer.geometryType(), 99
                )
                best_match_distance = self._get_distance_to_feature_on_layer(
                    result.mLayer,
                    result.mFeature,
                    origin_map_coordinates,
                )

        return best_match
