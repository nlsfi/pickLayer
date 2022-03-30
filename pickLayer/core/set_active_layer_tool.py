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
        layer_type: QgsMapToolIdentify.Type = QgsMapToolIdentify.AllLayers,
    ) -> None:

        self.layer_type = layer_type
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
            mode=self.TopDownAll,
            layerList=[],
            layerType=self.layer_type,
        )

        self.restoreCanvasPropertiesOverrides()

        layer_to_activate = self._choose_layer_from_identify_results(results)

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

    def _choose_layer_from_identify_results(
        self, results: QgsMapToolIdentify.IdentifyResult
    ) -> Optional[QgsMapLayer]:

        # Preserve IdentifyResult order
        resulting_layers = [result.mLayer for result in results]
        if len(results) == 0:
            return None
        else:
            return self._choose_layer(resulting_layers)

    def _choose_layer(self, layers: List[QgsMapLayer]) -> QgsMapLayer:
        """
        Picks one layer from input layers (may contain duplicates) in
        following order: point, line, polygon, other layers
        """
        preferred_geometry_type_order = {
            QgsWkbTypes.PointGeometry: 1,
            QgsWkbTypes.LineGeometry: 2,
            QgsWkbTypes.PolygonGeometry: 3,
        }

        return sorted(
            layers,
            key=lambda layer: preferred_geometry_type_order.get(
                layer.geometryType(), 99
            )
            if isinstance(layer, QgsVectorLayer)
            else 99,
        )[0]
