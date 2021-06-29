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

import pytest

from pickLayer.definitions.settings import Settings
from pickLayer.qgis_plugin_tools.tools.custom_logging import (
    LogTarget,
    get_log_level_key,
    get_log_level_name,
)
from pickLayer.qgis_plugin_tools.tools.settings import set_setting
from pickLayer.ui.settings_dialog import SettingsDialog

ORIGINAL_RADIUS = 1.5


@pytest.fixture
def settings_dialog(initialize_ui, qtbot):
    # Setup
    Settings.search_radius.set(ORIGINAL_RADIUS)
    set_setting(get_log_level_key(LogTarget.FILE), "INFO")

    settings_dialog = SettingsDialog()
    settings_dialog.show()
    qtbot.addWidget(settings_dialog)
    return settings_dialog


def test_set_search_radius(settings_dialog, qtbot):
    qtbot.keyClicks(settings_dialog.spin_box_search_radius, "21.5")

    assert Settings.search_radius.get() == 21.5


def test_set_log_level(settings_dialog, qtbot):
    qtbot.mouseMove(settings_dialog.combo_box_log_level_file)
    qtbot.keyClicks(settings_dialog.combo_box_log_level_file, "D")

    assert get_log_level_name(LogTarget.FILE) == "DEBUG"
