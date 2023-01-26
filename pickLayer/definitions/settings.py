#  Copyright (C) 2014-2019 Enrico Ferreguti (enricofer@gmail.com)
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

import enum
from typing import Any, Union

from qgis_plugin_tools.tools.settings import get_setting, set_setting


class Settings(enum.Enum):
    identify_tool_search_radius = "Map/searchRadiusMM"  # QGIS setting key
    # No default value, if this is not set, use the same value as identify tool
    search_radius = -1.0

    def get(self, typehint: type = str) -> Any:
        """Gets the value of the setting"""
        if self == Settings.identify_tool_search_radius:
            value = get_setting(self.value, internal=False)
        elif self == Settings.search_radius:
            # If not set, use the same value as Identify Tool
            value = get_setting(
                self.name,
                get_setting(
                    Settings.identify_tool_search_radius.value,
                    typehint=float,
                    internal=False,
                ),
                typehint=float,
            )
        else:
            value = get_setting(self.name, self.value, typehint)
        return value

    def set(self, value: Union[str, int, float, bool]) -> bool:
        """Sets the value of the setting"""
        if self == Settings.identify_tool_search_radius:
            return set_setting(self.value, value, internal=False)
        return set_setting(self.name, value)


class KeyboardShortcut(enum.Enum):
    """
    Keyboard shortcuts.
    """

    PICK_ACTIVE_LAYER = "Shift+P"
