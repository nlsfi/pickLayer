import pytest
from qgis.core import QgsPointXY

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