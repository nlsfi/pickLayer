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

import logging
from typing import Callable, List, Optional

from qgis.core import QgsApplication, QgsPointXY
from qgis.gui import QgsGui, QgsMapTool
from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QToolButton, QWidget
from qgis.utils import iface

from pickLayer.core.picklayer import PickLayer
from pickLayer.core.set_active_layer_tool import SetActiveLayerTool
from pickLayer.definitions.settings import KeyboardShortcut
from pickLayer.qgis_plugin_tools.tools.custom_logging import (
    setup_logger,
    teardown_logger,
)
from pickLayer.qgis_plugin_tools.tools.i18n import setup_translation, tr
from pickLayer.qgis_plugin_tools.tools.resources import plugin_name, resources_path
from pickLayer.ui.settings_dialog import SettingsDialog

LOGGER = logging.getLogger(plugin_name())


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
        self.toolbar: Optional[QToolBar] = None
        self.menu = plugin_name()
        self.pick_layer_tool: Optional[PickLayer] = None
        self.pick_layer_action: Optional[QAction] = None
        self.set_active_layer_tool = SetActiveLayerTool(iface.mapCanvas())
        self.set_active_layer_action: Optional[QAction] = None

    def get_set_active_layer_tool_action(self) -> QAction:
        """
        Public method for getting action that sets active layer.

        Can be used to set shortcut key from other plugins.
        """
        return self.set_active_layer_action

    def set_search_layers_for_set_active_layer_tool(
        self, search_layers: Optional[List[str]] = None
    ) -> None:
        """
        Public method for setting search layers for set active layer tool.

        Can be used to set layers from another plugin.

        Args:
            search_layers: Layers to search features from. If None, all vector
              layers in project are used.
        """

        self.set_active_layer_tool.search_layer_ids = search_layers

    def set_active_layer_using_closest_feature(
        self,
        point_xy: QgsPointXY,
        search_radius: Optional[float] = None,
        search_layers: Optional[List[str]] = None,
    ) -> None:
        """
        Public method for setting layer active based on given map coordinates.

        If multiple features are found, active layer is selected using this order:
        vectorlayer(point), vectorlayer(linestring), vectorlayer(polygon),
        other layers.

        Args:
            point_xy: Map coordinates
            search_radius: Search radius to use in map units. By default uses
              search radius defined in PickLayer settings.
            search_layers: Layers to search features from. By default searches all
              vector layers in project.
        """

        self.set_active_layer_tool.set_active_layer_using_closest_feature(
            point_xy, search_radius, search_layers
        )

    def initGui(self) -> None:  # noqa N802
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.toolbar = iface.addToolBar(plugin_name())
        self.toolbar.setObjectName(plugin_name())

        self.pick_layer_action = self._add_action(
            resources_path("icons", "pick_layer.svg"),
            text=plugin_name(),
            callback=self._activate_pick_layer,
            parent=iface.mainWindow(),
            set_checkable=True,
            add_to_toolbar=True,
            keyboard_shortcut=None,
        )
        self._add_action(
            "",
            text=tr("Settings"),
            callback=self._open_settings_dialg,
            parent=iface.mainWindow(),
            add_to_toolbar=False,
            icon=QgsApplication.getThemeIcon("/propertyicons/settings.svg"),
        )

        self.set_active_layer_action = self._add_action(
            resources_path("icons", "pick_layer_lite.svg"),
            text=tr("Set active layer"),
            status_tip=tr("Set layer active based on closest feature"),
            callback=self._set_active_layer_tool_selected,
            parent=iface.mainWindow(),
            set_checkable=True,
            add_to_toolbar=True,
            keyboard_shortcut=KeyboardShortcut.PICK_ACTIVE_LAYER,
        )

        self.set_active_layer_tool.setAction(self.set_active_layer_action)

    def onClosePlugin(self) -> None:  # noqa N802
        """Cleanup necessary items here when plugin dockwidget is closed"""
        pass

    def unload(self) -> None:
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            iface.removePluginMenu(self.menu, action)
            iface.removeToolBarIcon(action)
            iface.unregisterMainWindowAction(action)

        teardown_logger(plugin_name())

        # Remove toolbar from QGIS by deleting it
        del self.toolbar

    def _add_action(
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
        keyboard_shortcut: Optional[KeyboardShortcut] = None,
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
        action.setObjectName(text)
        action.setCheckable(set_checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if (
            add_to_toolbar is True
            and not self._action_exists(self.toolbar, action)
            and self.toolbar is not None
        ):
            self.toolbar.addAction(action)

        if add_to_menu is True:
            iface.addPluginToMenu(self.menu, action)

        if keyboard_shortcut is not None:
            QgsGui.shortcutsManager().registerAction(action, keyboard_shortcut.value)

        self.actions.append(action)

        return action

    def _activate_pick_layer(self) -> None:
        """Activates pick layer tool"""
        self.pick_layer_tool = PickLayer()
        self.pick_layer_tool.map_tool.setAction(self.pick_layer_action)
        self.pick_layer_tool.set_map_tool()

    def _set_active_layer_tool_selected(self) -> None:
        """Activates set active layer tool"""
        if iface.mapCanvas().mapTool() is not None:
            current_map_tool: QgsMapTool = iface.mapCanvas().mapTool()
            LOGGER.debug(
                tr(
                    "Current map tool before activating Set Active Layer tool is {}",
                    current_map_tool.toolName(),
                )
            )
            self.set_active_layer_tool.previous_map_tool = current_map_tool
        iface.mapCanvas().setMapTool(self.set_active_layer_tool)

    def _open_settings_dialg(self) -> None:
        dlg = SettingsDialog(iface.mainWindow())
        dlg.open()

    def _action_exists(self, toolbar: QToolBar, action: QAction) -> bool:
        """Check if toolbar contains the action"""
        return any(
            item.defaultAction() is not None
            and item.defaultAction().objectName() == action.objectName()
            for item in toolbar.findChildren(QToolButton)
        )
