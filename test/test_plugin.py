import pytest

from pickLayer import classFactory


@pytest.fixture()
def plugin_initialized(mock_iface, qgis_iface):
    plugin = classFactory(qgis_iface)
    plugin.initGui()

    return plugin


def test_plugin_loads_and_unloads(plugin_initialized):
    plugin_initialized.unload()


def test_plugin_has_actions(plugin_initialized):
    # PickLayer
    assert len(plugin_initialized.toolbar.actions()) == 1
    # PickLayer, settings
    assert len(plugin_initialized.actions) == 2
