# type: ignore
# flake8: noqa ANN201
"""
This class contains fixtures and common helper function to keep the test files shorter
"""
from typing import Tuple

import pytest
from PyQt5.QtWidgets import QWidget
from qgis.core import QgsApplication
from qgis.gui import QgsMapCanvas

from picklayer.qgis_plugin_tools.testing.qgis_interface import QgisInterface
from picklayer.qgis_plugin_tools.testing.utilities import get_qgis_app
from picklayer.qgis_plugin_tools.tools.messages import MsgBar


@pytest.fixture(autouse=True, scope="session")
def initialize_qgis() -> Tuple[QgsApplication, QgsMapCanvas, QgisInterface, QWidget]:
    """Initializes qgis session for all tests"""
    yield get_qgis_app()


@pytest.fixture(scope="session")
def qgis_app(initialize_qgis) -> QgsApplication:
    return initialize_qgis[0]


@pytest.fixture(scope="session")
def canvas(initialize_qgis) -> QgsMapCanvas:
    return initialize_qgis[1]


@pytest.fixture(scope="session")
def iface(initialize_qgis) -> QgisInterface:
    return initialize_qgis[2]


@pytest.fixture(scope="session")
def qgis_parent(initialize_qgis) -> QWidget:
    return initialize_qgis[3]


@pytest.fixture(scope="function")
def new_project(iface) -> None:
    """
    Initializes new QGIS project by removing layers and relations etc.
    """
    yield iface.newProject()


@pytest.fixture
def initialize_ui(mocker) -> None:
    """ Throws unhandled exception even though it is caught with log_if_fails """

    def mock_msg_bar(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], Exception):
            raise args[1]

    mocker.patch.object(MsgBar, "exception", mock_msg_bar)
