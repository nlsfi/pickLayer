# -*- coding: utf-8 -*-

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
import os
import sys

from picklayer.qgis_plugin_tools.infrastructure.debugging import (  # noqa F401
    setup_debugpy,
    setup_ptvsd,
    setup_pydevd,
)

debugger = os.environ.get("QGIS_PLUGIN_USE_DEBUGGER", "").lower()
if debugger in {"debugpy", "ptvsd", "pydevd"}:
    # provide the path to debugger dependencies (possibly venv site_packages)
    if len(os.environ.get("QGIS_DEBUGGER_DEPENDENCY_PATH", "")) > 0:
        sys.path.append(os.environ.get("QGIS_DEBUGGER_DEPENDENCY_PATH", ""))
    locals()["setup_" + debugger]()


# noinspection PyPep8Naming
def classFactory(iface):  # noqa N802 QGS105
    """Load pickLayer class from file picklayer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from picklayer.plugin import Plugin

    return Plugin()
