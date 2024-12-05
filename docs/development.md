# Development of pickLayer plugin

The code for the plugin is in the [pickLayer](../pickLayer) folder. Make sure you have
required tools, such as
Qt with Qt Editor and Qt Linquist installed by following this
[tutorial](https://www.qgistutorials.com/en/docs/3/building_a_python_plugin.html#get-the-tools).

## Setting up development environment

* Create a venv that is aware of system QGIS libraries: `python -m venv .venv --system-site-packages`
  * On Windows OSGeo4W v2 installs use `<osgeo>/apps/PythonXX/python.exe`
  with [necessary patches](./osgeo-python-patch.md)
* Activate the venv
* Install the dependencies for runtime and development (testing & linting):
  `pip install -r requirements.txt -r requirements-dev.txt --no-deps --only-binary=:all:`
* Install pre-commit: `pre-commit install`
* Create a `.env` from `.env.example`, and configure at least the QGIS executable path
* Launch development QGIS: `qpdt s`

## Commit message style

Commit messages should follow [Conventional Commits notation](https://www.conventionalcommits.org/en/v1.0.0/#summary).

## Adding or editing source files

If you create or edit source files make sure that:

* they contain absolute imports:

    ```python

    from pickLayer.utils.exceptions import TestException # Good

    from ..utils.exceptions import TestException # Bad


    ```

* you consider adding test files for the new functionality

## Testing

Install python packages listed in [requirements-dev.txt](../requirements-dev.txt) to
the virtual environment and run tests with:

```shell script
pytest
```

## Translating with QT Linguistic

The translation files are in [i18n](../pickLayer/resources/i18n) folder. Translatable
content in python files is code such as `tr(u"Hello World")`.

You can open the .ts files you wish to translate with Qt Linguist, make the changes and compile the translations to .qm files.

## Release steps

When the branch is in a releasable state, trigger the `Create draft release` workflow from GitHub Actions. Pass the to-be-released version number as an input to the workflow.

Workflow creates two commits in the target branch, one with the release state and one with the post-release state. It also creates a draft release from the release state commit with auto-generated release notes. Check the draft release notes and modify those if needed. After the release is published, the tag will be created, release workflow will be triggered, and it publishes a new version to PyPI.

Note: if you created the release commits to a non-`main` branch (i.e. to a branch with an open pull request), only publish the release after the pull request has been merged to main branch. Change the commit hash on the draft release to point to the actual rebased commit on the main branch, instead of the now obsolete commit on the original branch. If the GUI dropdown selection won't show the new main branch commits, the release may need to be re-created manually to allow selecting the rebased commit hash.

[OSGeo4W issue]: <https://trac.osgeo.org/osgeo4w/ticket/692> <!-- markdownlint-disable MD053 -->
