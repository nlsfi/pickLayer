# CHANGELOG

## Unreleased

## [3.9.6] - 2023-06-16

- fix plugin versioning

## [3.9.5] - 2023-06-16

- fix layer order in set active layer tool

## [3.9.4] - 2023-02-08

- fix plugin packaging

## [3.9.3] - 2023-02-08

- update requirements to match qgis-plugin-dev-tools version

## [3.9.2] - 2023-02-08

- update qgis-plugin-dev-tools version in order to produce valid zip plugin

## [3.9.1] - 2023-02-07

- fix release workflow and create separate workflows for running tests and creating draft releases
- set development.md up-to-date

## 3.9.0 - 2023-01-27

- update icons (in order to increase distinguishability)
- remove qgis plugin tools git submodule and use it as python dependency
- update python dependencies

## 3.8.0 - 2022-12-14

- update icons
- add pre-commit hooks for markdown files' style checks and for checking that commit
  messages follow convention
- allow user to click on raster file without python error being launched

## 3.7.0 - 2022-09-27

- add possibility to define layers to search from for set active layer tool

## 3.6.0 - 2022-09-17

- add default shortcut for pick active layer action

## 3.5.0 - 2022-07-19

- add finnish translations

## 3.4.0 - 2022-06-29

- pick active by clicking now considers distance between same type of layers
- automatically return to previous map tool after successfull use of set active layer tool

## 3.3.0 - 2022-04-04

- adds a new tool to set active layer by clicking features on map
- if multiple layers are found, active layer is chosen in this order: point layer, line
  layer, polygon layer, other map layers

## 3.2.0 - 2021-06-29

- perform spatial operation on selected feature
- fix bugs: custom actions, copying features
- reformat using black, isort and flake8
- refactor to use qgis_plugin_tools
- add CI and CD pipelines

## 3.1.0 - 2018-07-05

- subtract geometry new feature
- merge with geometry new feature
- makeValid geometry new feature
- feature highlighting

## 3.0.0 - 2018-03-30

- code migration to QGIS3

## 2.3.0 - 2016-06-20

- attributes values in context submenu - with copy to clipboard of content
- configure snapping options issue fixed
- coords typo issue fixed

## 2.2.0 - 2015-06-12

- issue picking on line feature fixed

## 2.1.0 - 2015-05-15

- selected layer and feature infos
- copy area and length to clipboard
- change datasource issues fixed

## 2.0.0 - 2014-11-03

- layer commands added:
  - zoom to layer
  - change data source (experimental)
- feature commands added:
  - zoom to feature
  - copy feature and paste geometries and attributes
- other commands:
  - layer actions attached to context menu
[3.9.1]: <https://github.com/nlsfi/pickLayer/releases/tag/v3.9.1>
[3.9.2]: <https://github.com/nlsfi/pickLayer/releases/tag/v3.9.2>
[3.9.3]: <https://github.com/nlsfi/pickLayer/releases/tag/v3.9.3>
[3.9.4]: <https://github.com/nlsfi/pickLayer/releases/tag/v3.9.4>
[3.9.6]: https://github.com/nlsfi/pickLayer/releases/tag/v3.9.6
