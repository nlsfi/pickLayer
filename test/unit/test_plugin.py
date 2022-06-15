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
import pytest
from qgis.core import QgsPointXY
from qgis.gui import QgsMapTool

from pickLayer import classFactory


@pytest.fixture()
def plugin_initialized(mock_iface, qgis_iface):
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    return plugin


def test_plugin_loads_and_unloads(plugin_initialized):
    plugin_initialized.unload()


def test_plugin_has_actions(plugin_initialized):
    # PickLayer, SetActiveLayerTool
    assert len(plugin_initialized.toolbar.actions()) == 2
    # PickLayer, SetActiveLayerTool, settings
    assert len(plugin_initialized.actions) == 3


def test_get_set_active_layer_tool_action(plugin_initialized):
    assert (
        plugin_initialized.get_set_active_layer_tool_action().objectName()
        == "Set active layer"
    )


def test_set_active_layer_using_closest_feature_called(plugin_initialized, mocker):
    m_choose_layer_from_identify_results = mocker.patch.object(
        plugin_initialized.set_active_layer_tool,
        "_choose_layer_from_identify_results",
        return_value=None,
        autospec=True,
    )

    plugin_initialized.set_active_layer_using_closest_feature(
        QgsPointXY(100000, 200000)
    )

    m_choose_layer_from_identify_results.assert_called_once()


def test_set_active_layer_tool_selected_saves_current_map_tool_if_tool_present(
    qgis_iface, plugin_initialized
):
    dummy_map_tool = QgsMapTool(qgis_iface.mapCanvas())
    qgis_iface.mapCanvas().setMapTool(dummy_map_tool)
    assert plugin_initialized.set_active_layer_tool.previous_map_tool is None

    plugin_initialized._set_active_layer_tool_selected()

    assert plugin_initialized.set_active_layer_tool.previous_map_tool == dummy_map_tool


def test_set_active_layer_tool_selected_doesnt_save_current_map_tool_if_tool_not_present(
    qgis_iface, plugin_initialized
):
    assert plugin_initialized.set_active_layer_tool.previous_map_tool is None
    assert qgis_iface.mapCanvas().mapTool() is None

    plugin_initialized._set_active_layer_tool_selected()

    assert plugin_initialized.set_active_layer_tool.previous_map_tool is None
