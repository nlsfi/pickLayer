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
import webbrowser
from typing import Optional

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QDialog, QWidget

from picklayer.definitions.settings import Settings
from picklayer.qgis_plugin_tools.tools.custom_logging import (
    LogTarget,
    get_log_folder,
    get_log_level_key,
    get_log_level_name,
)
from picklayer.qgis_plugin_tools.tools.resources import load_ui, plugin_name
from picklayer.qgis_plugin_tools.tools.settings import set_setting

FORM_CLASS: QWidget = load_ui("settings_dialog.ui")

LOGGER = logging.getLogger(plugin_name())

LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SettingsDialog(QDialog, FORM_CLASS):
    """
    This file is originally adapted from
    https://github.com/GispoCoding/qaava-qgis-plugin licensed under GPL version 2
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QgsApplication.getThemeIcon("/propertyicons/settings.svg"))
        self._setup_settings()

    def _setup_settings(self) -> None:
        # Search radius
        self.spin_box_search_radius.setValue(Settings.search_radius.get())
        self.spin_box_search_radius.valueChanged.connect(
            lambda v: Settings.search_radius.set(float(v))
        )

        # Logging
        self.combo_box_log_level_file.addItems(LOGGING_LEVELS)
        self.combo_box_log_level_console.addItems(LOGGING_LEVELS)
        self.combo_box_log_level_file.setCurrentText(get_log_level_name(LogTarget.FILE))
        self.combo_box_log_level_console.setCurrentText(
            get_log_level_name(LogTarget.STREAM)
        )

        self.combo_box_log_level_file.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.FILE), level)
        )

        self.combo_box_log_level_console.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.STREAM), level)
        )

        self.btn_open_log.clicked.connect(
            lambda _: webbrowser.open(str(get_log_folder() / f"{plugin_name()}.log"))
        )
