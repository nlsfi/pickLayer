Development of pickLayer plugin
===========================


This project uses [qgis_plugin_tools](https://github.com/nlsfi/qgis_plugin_tools) submodule,
so set git setting value: `git config --global submodule.recurse true`.

When cloning use `--recurse-submodules` like so:
`git clone --recurse-submodules https://github.com/nlsfi/pickLayer.git`

When pulling from existing repo:
```sh
git submodule init
git submodule update
```


The code for the plugin is in the [pickLayer](../pickLayer) folder. Make sure you have required tools, such as
Qt with Qt Editor and Qt Linquist installed by following this
[tutorial](https://www.qgistutorials.com/en/docs/3/building_a_python_plugin.html#get-the-tools).

For building the plugin use platform independent [build.py](../pickLayer/build.py) script.

## Setting up development environment

* Create a venv that is aware of system QGIS libraries: `python -m venv .venv --system-site-packages`
  * On Windows OSGeo4W v2 installs use `<osgeo>/apps/PythonXX/python.exe` with [necessary patches](./osgeo-python-patch.md)
* Activate the venv
* Install the dependencies for runtime and development (testing & linting): `pip install -r requirements.txt -r requirements-dev.txt`
* Create a `.env` from `.env.example`, and configure at least the QGIS executable path
* Launch development QGIS: `qpdt s`

## Adding or editing  source files

If you create or edit source files make sure that:

* they contain absolute imports:
    ```python

    from pickLayer.utils.exceptions import TestException # Good

    from ..utils.exceptions import TestException # Bad


    ```
* they will be found by [build.py](../pickLayer/build.py) script (`py_files` and `ui_files` values)
* you consider adding test files for the new functionality

## Deployment

Edit [build.py](../pickLayer/build.py) to contain working values for *profile*, *lrelease* and *pyrcc*. If you are
running on Windows, make sure the value *QGIS_INSTALLATION_DIR* points to right folder

Run the deployment with:

```shell script
python build.py deploy
```

After deploying and restarting QGIS you should see the plugin in the QGIS installed plugins where you have to activate
it.

## Testing

Install python packages listed in [requirements-dev.txt](../requirements-dev.txt) to the virtual environment
and run tests with:

```shell script
pytest
```

## Translating

### Translating with Transifex

Fill in `transifex_coordinator` (Transifex username) and `transifex_organization`
in [.qgis-plugin-ci](../.qgis-plugin-ci) to use Transifex translation.

If you want to see the translations during development, add `i18n` to the `extra_dirs` in `build.py`:

```python
extra_dirs = ["resources", "i18n"]
```

#### Pushing / creating new translations

For step-by-step instructions, read the [translation tutorial](./translation_tutorial.md#Tutorial).

* First, install [Transifex CLI](https://docs.transifex.com/client/installing-the-client) and
  [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci)
* Make sure command `pylupdate5` works. Otherwise install it with `pip install pyqt5`
* Run `qgis-plugin-ci push-translation <your-transifex-token>`
* Go to your Transifex site, add some languages and start translating
* Copy [push_translations.yml](push_translations.yml) file to [workflows](../.github/workflows) folder to enable
  automatic pushing after commits to master
* Add this badge ![](https://github.com/nlsfi/pickLayer/workflows/Translations/badge.svg) to
  the [README](../README.md)

##### Pulling

There is no need to pull if you configure `--transifex-token` into your
[release](../.github/workflows/release.yml) workflow (remember to use Github Secrets). Remember to uncomment the
lrelease section as well. You can however pull manually to test the process.

* Run `qgis-plugin-ci pull-translation --compile <your-transifex-token>`

#### Translating with QT Linguistic (if Transifex not available)

The translation files are in [i18n](../pickLayer/resources/i18n) folder. Translatable content in python files is
code such as `tr(u"Hello World")`.

To update language *.ts* files to contain newest lines to translate, run

```shell script
python build.py transup
```

You can then open the *.ts* files you wish to translate with Qt Linguist and make the changes.

Compile the translations to *.qm* files with:

```shell script
python build.py transcompile
```

### Github Release

Follow these steps to create a release

* Add changelog information to [CHANGELOG.md](../CHANGELOG.md) using this
  [format](https://raw.githubusercontent.com/opengisch/qgis-plugin-ci/master/CHANGELOG.md)
* Make a new commit. (`git add -A && git commit -m "Release 0.1.0"`)
* Create new tag for it (`git tag -a 0.1.0 -m "Version 0.1.0"`)
* Push tag to Github using `git push --follow-tags`
* Create Github release
* [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) adds release zip automatically as an asset

Modify [release](../.github/workflows/release.yml) workflow according to its comments if you want to upload the
plugin to QGIS plugin repository.

### Local release

For local release install [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) (possibly to different venv
to avoid Qt related problems on some environments) and follow these steps:
```shell
cd pickLayer
qgis-plugin-ci package --disable-submodule-update 0.1.0
```
