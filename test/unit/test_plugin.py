import pytest
from qgis.core import QgsPointXY
from qgis.PyQt.QtCore import QPoint

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


def test_set_active_layer_using_closest_feature_should_convert_input_to_map_canvas_xy(
    plugin_initialized, qgis_iface, mocker
):
    m_set_active_layer_using_closest_feature = mocker.patch.object(
        plugin_initialized.set_active_layer_tool,
        "set_active_layer_using_closest_feature",
        return_value=None,
        autospec=True,
    )

    coordinates = QgsPointXY(100000, 200000)

    plugin_initialized.set_active_layer_using_closest_feature(coordinates)

    x, y, _ = m_set_active_layer_using_closest_feature.call_args.args

    result_as_point_xy = (
        qgis_iface.mapCanvas().getCoordinateTransform().toMapCoordinates(QPoint(x, y))
    )

    assert result_as_point_xy.x() == coordinates.x()
    assert result_as_point_xy.y() == coordinates.y()
