# PickLayer

![tests](https://github.com/nlsfi/pickLayer/workflows/Tests/badge.svg)
[![codecov.io](https://codecov.io/github/nlsfi/pickLayer/coverage.svg?branch=main)](https://codecov.io/github/nlsfi/pickLayer?branch=main)
![release](https://github.com/nlsfi/pickLayer/workflows/Release/badge.svg)
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Set layer properties and options straight from map canvas. Activate layer by clicking
features on map.

Originally created and maintained by [enricofer](https://github.com/enricofer)
in <https://github.com/enricofer/pickLayer>.

## Usage from other plugins

It is possible to control SetActiveLayerTool programmatically using public methods
defined in Plugin-class.

```python
from qgis.core import QgsPointXY
from qgis.utils import plugins

some_point = QgsPointXY(123, 456)

# Activates layer if features are found near given point
plugins["pickLayer"].set_active_layer_using_closest_feature(point_xy=some_point)

# Activates layer with custom search radius (in map units)
plugins["pickLayer"].set_active_layer_using_closest_feature(point_xy=some_point, search_radius=100)

# Activates layer using subset of layers (expects layer ids)
plugins["pickLayer"].set_active_layer_using_closest_feature(point_xy=some_point, search_layers=["layer-1", "layer-2"])

# Set search layers for set active layer map tool (expects layer ids)
plugins["pickLayer"].set_search_layers_for_set_active_layer_tool_action(search_layers=["layer-1", "layer-2"])

# Reset search layers for set active layer map tool (will use all vector layers in project)
plugins["pickLayer"].set_search_layers_for_set_active_layer_tool_action(search_layers=None)

# Get action for e.g. defining shortcut key programmatically
action = plugins["pickLayer"].get_set_active_layer_tool_action()
# action.do_something()

```

## Development

Refer to [development](docs/development.md) for developing this QGIS3 plugin.

## License

This plugin is licenced with
[GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html).
See [LICENSE](LICENSE) for more information.
