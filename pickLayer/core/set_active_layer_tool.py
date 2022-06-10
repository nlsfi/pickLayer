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
    QgsRenderContext,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapToolIdentify
from qgis.PyQt.QtCore import QPoint
from qgis.PyQt.QtGui import QCursor
from qgis.utils import iface

from pickLayer.definitions.settings import Settings
from pickLayer.qgis_plugin_tools.tools.i18n import tr
from pickLayer.qgis_plugin_tools.tools.messages import MsgBar
from pickLayer.qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class SetActiveLayerTool(QgsMapToolIdentify):
    """
    Map tool for selecting feature and its versions.
    """

    def __init__(
        self,
        canvas: QgsMapCanvas,
    ) -> None:
        super().__init__(canvas)
        self.setCursor(QCursor())

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
        self, location: QgsPointXY, search_radius: Optional[float] = None
    ) -> None:

        if search_radius is None:
            search_radius = self._get_default_search_radius()

        self.setCanvasPropertiesOverrides(search_radius)

        results = self.identify(
            geometry=QgsGeometry.fromPointXY(location),
            mode=QgsMapToolIdentify.TopDownAll,
            layerType=QgsMapToolIdentify.AllLayers,
        )

        self.restoreCanvasPropertiesOverrides()

        layer_to_activate = self._choose_layer_from_identify_results(results, location)

        if layer_to_activate is not None:
            LOGGER.info(tr("Activating layer {}", layer_to_activate.name()))
            iface.setActiveLayer(layer_to_activate)

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

        type_preference = {
            QgsWkbTypes.PointGeometry: 3,
            QgsWkbTypes.LineGeometry: 2,
            QgsWkbTypes.PolygonGeometry: 1,
        }

        best_match: Optional[QgsVectorLayer] = None
        best_match_type_preference = 0
        best_match_distance = 0.0

        for result in results:
            # sanity check even if identify type is vector layer, helps with type hints
            if not isinstance(result.mLayer, QgsVectorLayer):
                continue

            if (
                best_match is None
                or type_preference.get(result.mLayer.geometryType(), 0)
                > best_match_type_preference
                or (
                    type_preference.get(result.mLayer.geometryType(), 0)
                    == best_match_type_preference
                    and self._get_distance_to_feature_on_layer(
                        result.mLayer, result.mFeature, origin_map_coordinates
                    )
                    < best_match_distance
                )
            ):
                best_match = result.mLayer
                best_match_type_preference = type_preference.get(
                    result.mLayer.geometryType(), 0
                )
                best_match_distance = self._get_distance_to_feature_on_layer(
                    result.mLayer,
                    result.mFeature,
                    origin_map_coordinates,
                )

        return best_match
