# -*- coding: utf-8 -*-

#  Copyright (C) 2022 National Land Survey of Finland
#  (https://www.maanmittauslaitos.fi/en).
#
#
#  This file is part of PickLayer.
#
#  PickLayer  is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SpatialDataPackageExport is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PickLayer. If not, see <https://www.gnu.org/licenses/>.
import logging
from collections import OrderedDict
from typing import Dict, List, Optional, cast

from qgis.core import QgsMapLayer, QgsVectorLayer, QgsWkbTypes
from qgis.gui import QgsMapCanvas, QgsMapToolIdentify
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

    def __init__(self, canvas: QgsMapCanvas, layer_type: str = "AllLayers") -> None:

        self.layer_type = getattr(QgsMapToolIdentify, layer_type)
        self.canvas = canvas
        QgsMapToolIdentify.__init__(self, canvas)
        self.setCursor(QCursor())

    def canvasReleaseEvent(self, mouse_event) -> None:  # noqa N802
        orig_search_radius = Settings.identify_tool_search_radius.get()
        try:
            search_radius = Settings.search_radius.get()
            LOGGER.debug(f"Setting search radius to {search_radius}")
            Settings.identify_tool_search_radius.set(search_radius)

            self.set_active_layer_using_closest_feature(
                mouse_event.x(), mouse_event.y()
            )
        except Exception as e:
            MsgBar.exception(
                tr("Error occurred: {}", str(e)), tr("Check log for more details.")
            )
        finally:
            Settings.identify_tool_search_radius.set(orig_search_radius)

    def set_active_layer_using_closest_feature(
        self, mouse_x: int, mouse_y: int, search_radius: Optional[float] = None
    ) -> None:

        if search_radius is not None:
            self.setCanvasPropertiesOverrides(search_radius)

        results = self.identify(
            mouse_x, mouse_y, self.TopDownAll, [], layerType=self.layer_type
        )

        if search_radius is not None:
            self.restoreCanvasPropertiesOverrides()

        layer_to_activate = self._choose_layer_from_identify_results(results)

        if layer_to_activate is not None:
            LOGGER.info(tr("Activating layer {}", layer_to_activate.name()))
            iface.setActiveLayer(layer_to_activate)

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
        if len(layers) == 1:
            return layers[0]
        else:
            closest_layers: Dict[str, Optional[QgsMapLayer]] = OrderedDict()
            closest_layers[QgsWkbTypes.PointGeometry] = None
            closest_layers[QgsWkbTypes.LineGeometry] = None
            closest_layers[QgsWkbTypes.PolygonGeometry] = None
            closest_layers["closest_other_layer"] = None

            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer:
                    layer = cast(QgsVectorLayer, layer)
                    geometry_type = layer.geometryType()

                    if closest_layers[geometry_type] is None:
                        closest_layers[geometry_type] = layer

                    elif (
                        geometry_type
                        not in [
                            QgsWkbTypes.PointGeometry,
                            QgsWkbTypes.LineGeometry,
                            QgsWkbTypes.PolygonGeometry,
                        ]
                        and closest_layers["closest_other_layer"] is None
                    ):
                        closest_layers["closest_other_layer"] = layer

                else:
                    if closest_layers["closest_other_layer"] is None:
                        closest_layers["closest_other_layer"] = layer

            for layer in closest_layers.values():
                if layer is not None:
                    return layer
