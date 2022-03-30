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

# type: ignore
# flake8: noqa ANN201
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
