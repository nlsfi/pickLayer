#  Copyright (C) 2014-2019 Enrico Ferreguti (enricofer@gmail.com)
#  Copyright (C) 2021 National Land Survey of Finland
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PickLayer.  If not, see <https://www.gnu.org/licenses/>.

import logging

from qgis.core import QgsFeature, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapToolIdentify
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor

# from cursor import Cursor
from pickLayer.definitions.settings import Settings
from pickLayer.qgis_plugin_tools.tools.i18n import tr
from pickLayer.qgis_plugin_tools.tools.messages import MsgBar
from pickLayer.qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class IdentifyGeometry(QgsMapToolIdentify):
    geom_identified = pyqtSignal(QgsVectorLayer, QgsFeature)

    def __init__(
        self, canvas: QgsMapCanvas, layerType: str = "AllLayers"  # noqa N803
    ) -> None:
        self.layer_type = getattr(QgsMapToolIdentify, layerType)
        self.canvas = canvas
        QgsMapToolIdentify.__init__(self, canvas)
        self.setCursor(QCursor())

    def canvasReleaseEvent(self, mouse_event) -> None:  # noqa N802
        orig_search_radius = Settings.identify_tool_search_radius.get()
        try:
            search_radius = Settings.search_radius.get()
            LOGGER.debug(f"Setting search radius to {search_radius}")
            Settings.identify_tool_search_radius.set(search_radius)
            results = self.identify(
                mouse_event.x(), mouse_event.y(), self.LayerSelection, self.layer_type
            )
        except Exception as e:
            MsgBar.exception(
                tr("Error occurred: {}", str(e)), tr("Check log for more details.")
            )
            results = []
        finally:
            Settings.identify_tool_search_radius.set(orig_search_radius)

        if len(results) > 0:
            LOGGER.debug("Feature found")
            self.geom_identified.emit(
                results[0].mLayer, QgsFeature(results[0].mFeature)
            )
