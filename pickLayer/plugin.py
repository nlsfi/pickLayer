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

from typing import Callable, List, Optional

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QWidget
from qgis.utils import iface

from pickLayer.core.picklayer import PickLayer
from pickLayer.qgis_plugin_tools.tools.custom_logging import (
    setup_logger,
    teardown_logger,
)
from pickLayer.qgis_plugin_tools.tools.i18n import setup_translation, tr
from pickLayer.qgis_plugin_tools.tools.resources import plugin_name, resources_path
from pickLayer.ui.settings_dialog import SettingsDialog


class Plugin:
    """QGIS Plugin Implementation."""

    def __init__(self) -> None:
        setup_logger(plugin_name())

        # initialize locale
        locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass

        self.actions: List[QAction] = []
        self.menu = tr(plugin_name())
        self.pick_layer: Optional[PickLayer] = None
        self.pick_layer_action: Optional[QAction] = None

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Callable,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        set_checkable: bool = False,
        status_tip: Optional[str] = None,
        whats_this: Optional[str] = None,
        parent: Optional[QWidget] = None,
        icon: Optional[QIcon] = None,
    ) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path) if icon is None else icon
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(set_checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            iface.addToolBarIcon(action)

        if add_to_menu:
            iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self) -> None:  # noqa N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.pick_layer_action = self.add_action(
            resources_path("icons", "pickLayer.png"),
            text=plugin_name(),
            callback=self.run,
            parent=iface.mainWindow(),
            set_checkable=True,
        )
        self.add_action(
            "",
            text=tr("Settings"),
            callback=self.open_settings_dialg,
            parent=iface.mainWindow(),
            add_to_toolbar=False,
            icon=QgsApplication.getThemeIcon("/propertyicons/settings.svg"),
        )

    def onClosePlugin(self) -> None:  # noqa N802
        """Cleanup necessary items here when plugin dockwidget is closed"""
        pass

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            iface.removePluginMenu(plugin_name(), action)
            iface.removeToolBarIcon(action)
        teardown_logger(plugin_name())

    def run(self) -> None:
        """Run method that performs all the real work"""
        self.pick_layer = PickLayer()
        self.pick_layer.map_tool.setAction(self.pick_layer_action)
        self.pick_layer.set_map_tool()

    def open_settings_dialg(self) -> None:
        dlg = SettingsDialog(iface.mainWindow())
        dlg.open()
