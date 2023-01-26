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

from typing import List, Tuple
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from pytest_qgis import QgisInterface
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsVectorLayerUtils,
)
from qgis.gui import QgsMapTool, QgsMapToolIdentify
from qgis_plugin_tools.tools.resources import plugin_test_data_path

from pickLayer.core.set_active_layer_tool import SetActiveLayerTool
from pickLayer.definitions.settings import Settings

MOUSE_LOCATION = QgsPointXY(0, 0)


def create_identify_result(
    identified_feature_geom_wtks: List[Tuple[str, str, str]]
) -> List[QgsMapToolIdentify.IdentifyResult]:
    results = []

    for wkt, crs, layer_name in identified_feature_geom_wtks:
        geometry = QgsGeometry.fromWkt(wkt)
        layer = QgsMemoryProviderUtils.createMemoryLayer(
            layer_name,
            QgsFields(),
            geometry.wkbType(),
            QgsCoordinateReferenceSystem(crs),
        )
        feature = QgsVectorLayerUtils.createFeature(layer, geometry, {})
        layer.dataProvider().addFeature(feature)

        # using the actual QgsMapToolIdentify.IdentifyResult causes
        # fatal exceptions, mock probably is sufficient for testing
        results.append(MagicMock(**{"mLayer": layer, "mFeature": feature}))

    return results


@pytest.fixture()
def map_tool(qgis_iface):
    return SetActiveLayerTool(qgis_iface.mapCanvas())


@pytest.fixture(scope="session")
def test_layers():
    layers = [
        QgsVectorLayer("PointZ", "point_layer", "memory"),
        QgsVectorLayer("LineStringZ", "line_layer", "memory"),
        QgsVectorLayer("PolygonZ", "polygon_layer", "memory"),
    ]

    wkt_geom_collection = [
        ("PointZ (-1 0 0)", "PointZ (-2 0 0)"),
        ("LineStringZ (1 0 0, 1 5 0)", "LineStringZ (2 0 0, 2 5 0)"),
        (
            "PolygonZ ((1 1 0, 1 2 0, 2 2 0, 2 1 0, 1 1 0))",
            "PolygonZ ((2 0 0, 2 3 0, 3 3 0, 3 0 0, 2 0 0))",
        ),
    ]

    for layer, wkt_geoms in zip(layers, wkt_geom_collection):
        features = [
            QgsVectorLayerUtils.createFeature(layer, QgsGeometry.fromWkt(wkt_geoms[0])),
            QgsVectorLayerUtils.createFeature(layer, QgsGeometry.fromWkt(wkt_geoms[1])),
        ]

        assert all(not feature.geometry().isNull() for feature in features)
        success, _ = layer.dataProvider().addFeatures(features)
        assert success

        QgsProject.instance().addMapLayer(layer)
    return layers


@pytest.mark.parametrize(
    argnames=(
        "search_radius",
        "expected_num_results",
    ),
    argvalues=[
        (0.5, 0),
        (1.5, 3),
        (2.5, 6),
    ],
    ids=[
        "radius-0.5m-none-found",
        "radius-1.5m-half-found",
        "radius-2.5m-all-found",
    ],
)
def test_set_active_layer_using_closest_feature(
    map_tool,
    test_layers,
    search_radius,
    expected_num_results,
    mocker,
):
    m_choose_layer_from_identify_results = mocker.patch.object(
        map_tool,
        "_choose_layer_from_identify_results",
        return_value=None,
        autospec=True,
    )

    map_tool.set_active_layer_using_closest_feature(MOUSE_LOCATION, search_radius)

    identify_results = m_choose_layer_from_identify_results.call_args.args[0]
    assert len(identify_results) == expected_num_results


@pytest.mark.parametrize(
    argnames=(
        "search_layers",
        "expected_num_results",
    ),
    argvalues=[
        ([0], 2),
        ([0, 1], 4),
        ([0, 1, 2], 6),
    ],
    ids=[
        "features-from-one-layer-found",
        "features-from-two-layers-found",
        "features-from-three-layers-found",
    ],
)
def test_set_active_layer_using_closest_feature_with_search_layers(
    map_tool,
    test_layers,
    search_layers,
    expected_num_results,
    mocker,
):
    map_tool.search_layer_ids = ["these-should-be-overridden", "id2"]

    layer_ids = []

    for index in search_layers:
        layer_ids.append(test_layers[index].id())

    m_choose_layer_from_identify_results = mocker.patch.object(
        map_tool,
        "_choose_layer_from_identify_results",
        return_value=None,
        autospec=True,
    )

    map_tool.set_active_layer_using_closest_feature(
        MOUSE_LOCATION, search_radius=2.5, search_layer_ids=layer_ids
    )

    identify_results = m_choose_layer_from_identify_results.call_args.args[0]
    assert len(identify_results) == expected_num_results


def test_set_active_layer_using_closest_feature_with_search_layers_set_to_none_should_find_all(
    map_tool,
    test_layers,
    mocker,
):
    m_choose_layer_from_identify_results = mocker.patch.object(
        map_tool,
        "_choose_layer_from_identify_results",
        return_value=None,
        autospec=True,
    )

    map_tool.set_active_layer_using_closest_feature(
        MOUSE_LOCATION, search_radius=2.5, search_layer_ids=None
    )

    identify_results = m_choose_layer_from_identify_results.call_args.args[0]
    assert len(identify_results) == 6


def test_get_default_search_radius_changes_if_settings_changed(
    map_tool,
):
    Settings.search_radius.set(0)
    radius = map_tool._get_default_search_radius()

    assert radius == 0

    Settings.search_radius.set(2)
    radius_after_settings_changed = map_tool._get_default_search_radius()

    assert radius_after_settings_changed > radius


def test_set_active_layer_using_closest_feature_sets_returned_layer_active(
    map_tool,
    qgis_iface,
    mocker,
):
    mock_return_layer = QgsVectorLayer("PointZ", "point_layer", "memory")
    m_choose_layer_from_identify_results = mocker.patch.object(
        map_tool,
        "_choose_layer_from_identify_results",
        return_value=mock_return_layer,
        autospec=True,
    )
    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(MOUSE_LOCATION)

    m_choose_layer_from_identify_results.assert_called_once()
    assert m_set_active_layer.call_args.args[0] == mock_return_layer


def test_set_active_layer_using_closest_feature_does_nothing_if_layer_not_found(
    map_tool,
    qgis_iface,
    mocker,
):
    m_choose_layer_from_identify_results = mocker.patch.object(
        map_tool,
        "_choose_layer_from_identify_results",
        return_value=None,
        autospec=True,
    )
    # Spy is used instead of patch in order to double check setActiveLayer is never called
    spy_activate_layer_and_previous_map_tool = mocker.spy(
        map_tool, "_activate_layer_and_previous_map_tool"
    )
    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(MOUSE_LOCATION)

    m_choose_layer_from_identify_results.assert_called_once()
    spy_activate_layer_and_previous_map_tool.assert_not_called()
    m_set_active_layer.assert_not_called()


def test_preferred_type_chosen_from_different_types(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
):
    results = create_identify_result(
        [
            ("POINT(3 3)", "EPSG:3067", "point"),
            ("LINESTRING(4 4, 5 5)", "EPSG:3067", "line"),
            ("POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))", "EPSG:3067", "polygon"),
        ]
    )

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:3067"))

    mocker.patch.object(map_tool, "identify", return_value=results)

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(QgsPointXY(-1, -1))

    m_set_active_layer.assert_called_once()

    args, _ = m_set_active_layer.call_args_list[0]
    call_layer = args[0]
    assert call_layer.name() == "point"


def test_closest_of_same_type_chosen(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
):
    results = create_identify_result(
        [
            ("POINT(3 3)", "EPSG:3067", "point-mid"),
            ("POINT(2 2)", "EPSG:3067", "point-close"),
            ("POINT(4 4)", "EPSG:3067", "point-far"),
        ]
    )

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:3067"))
    map_tool.canvas().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3067"))

    mocker.patch.object(map_tool, "identify", return_value=results)

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(QgsPointXY(1, 1))

    m_set_active_layer.assert_called_once()

    args, _ = m_set_active_layer.call_args_list[0]
    call_layer = args[0]
    assert call_layer.name() == "point-close"


def test_closest_of_same_type_chosen_even_if_project_and_layer_crs_differs(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
    qgis_new_project,
):
    results = create_identify_result(
        [
            # points close to 250000,6700000 in 3067 in different crs's
            ("POINT(22.46220271 60.35440884)", "EPSG:4326", "point-far"),
            ("POINT(2415468 6694753)", "EPSG:2392", "point-mid"),
            ("POINT(2501177 8479351)", "EPSG:3857", "point-close"),
        ]
    )

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:3067"))
    map_tool.canvas().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3067"))

    mocker.patch.object(map_tool, "identify", return_value=results)

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(QgsPointXY(250000, 6700000))

    m_set_active_layer.assert_called_once()

    args, _ = m_set_active_layer.call_args_list[0]
    call_layer = args[0]
    assert call_layer.name() == "point-close"


def test_line_crossing_origin_chosen_as_closest(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
    qgis_new_project,
):
    results = create_identify_result(
        [
            ("LINESTRING(1.1 1.1, 2 2)", "EPSG:3067", "line-not-crossing"),
            ("LINESTRING(0 2, 2 0)", "EPSG:3067", "line-crossing"),
        ]
    )

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:3067"))
    map_tool.canvas().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3067"))

    mocker.patch.object(map_tool, "identify", return_value=results)

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(QgsPointXY(1, 1))

    m_set_active_layer.assert_called_once()

    args, _ = m_set_active_layer.call_args_list[0]
    call_layer = args[0]
    assert call_layer.name() == "line-crossing"


def test_top_polygon_chosen_from_multiple_nested_even_if_top_not_closest(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
    qgis_new_project,
):
    results = create_identify_result(
        [
            ("POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))", "EPSG:3067", "polygon-0-10"),
            ("POLYGON((0 -5, 0 5, 5 5, 5 -5, 0 -5))", "EPSG:3067", "polygon-5-5"),
        ]
    )

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:3067"))
    map_tool.canvas().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:3067"))

    mocker.patch.object(map_tool, "identify", return_value=results)

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    # emulate click near the corner of 5-5 and close to center of 10-10
    map_tool.set_active_layer_using_closest_feature(QgsPointXY(4.9, 4.9))

    m_set_active_layer.assert_called_once()

    args, _ = m_set_active_layer.call_args_list[0]
    call_layer = args[0]
    assert call_layer.name() == "polygon-0-10"


def test_only_raster_present_no_change_active_layer(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
    qgis_new_project,
):
    # raster file is 1,1 -> 2,2 bbox in 4326 crs
    raster_file = plugin_test_data_path("raster", "simple_raster_layer.tif")
    raster_layer = QgsRasterLayer(raster_file)
    QgsProject.instance().addMapLayer(raster_layer)

    QgsProject.instance().setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
    map_tool.canvas().setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

    m_set_active_layer = mocker.patch.object(
        qgis_iface, "setActiveLayer", return_value=None
    )

    map_tool.set_active_layer_using_closest_feature(QgsPointXY(1.5, 1.5))

    m_set_active_layer.assert_not_called()


def test_activate_layer_and_previous_map_tool_activates_previous_map_tool(
    map_tool: SetActiveLayerTool, mocker: MockerFixture, qgis_iface: QgisInterface
):
    m_logger_info = mocker.patch("pickLayer.core.set_active_layer_tool.LOGGER.info")
    dummy_map_tool = QgsMapTool(qgis_iface.mapCanvas())
    map_tool.previous_map_tool = dummy_map_tool
    assert qgis_iface.mapCanvas().mapTool() is None

    map_tool._activate_layer_and_previous_map_tool(MagicMock())

    m_logger_info.assert_not_called()
    assert qgis_iface.mapCanvas().mapTool() == dummy_map_tool


def test_activate_layer_and_previous_map_tool_doesnt_change_tool_when_previous_not_found(
    map_tool: SetActiveLayerTool,
    mocker: MockerFixture,
    qgis_iface: QgisInterface,
):
    m_logger_info = mocker.patch("pickLayer.core.set_active_layer_tool.LOGGER.info")
    m_iface_mapcanvas = mocker.patch(
        "pickLayer.core.set_active_layer_tool.iface.mapCanvas"
    )
    assert map_tool.previous_map_tool is None

    map_tool._activate_layer_and_previous_map_tool(MagicMock())

    m_logger_info.assert_called_once()
    m_iface_mapcanvas.assert_not_called()
