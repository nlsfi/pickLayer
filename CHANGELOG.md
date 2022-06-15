# CHANGELOG

## Unreleased

- pick active by clicking now considers distance between same type of layers
- automatically return to previous map tool after successfull use of set active layer tool

## 3.3.0 - 2022-04-04

- adds a new tool to set active layer by clicking features on map
- if multiple layers are found, active layer is chosen in this order: point layer, line layer, polygon layer, other map layers

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
