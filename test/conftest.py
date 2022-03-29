# type: ignore
# flake8: noqa ANN201
"""
This class contains fixtures and common helper function to keep the test files shorter
"""

import pytest
from qgis.PyQt.QtWidgets import QToolBar

from pickLayer.qgis_plugin_tools.tools.messages import MsgBar


@pytest.fixture()
def initialize_ui(mocker) -> None:
    """ Throws unhandled exception even though it is caught with log_if_fails """

    def mock_msg_bar(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], Exception):
            raise args[1]

    mocker.patch.object(MsgBar, "exception", mock_msg_bar)


@pytest.fixture(scope="session")
def mock_iface(session_mocker, qgis_iface, qgis_parent) -> None:
    qgis_iface.removePluginMenu = lambda *args: None
    qgis_iface.unregisterMainWindowAction = lambda *args: None
    session_mocker.patch.object(qgis_iface, "addToolBar", lambda *args: QToolBar(*args))
