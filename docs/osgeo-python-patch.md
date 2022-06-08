# Windows OSGeo4W v2 installer Python environment patches

This patching makes the default executable in `<osgeo>/apps/PythonXX/python.exe` to resolve QGIS and PyQt imports correctly with `import qgis` pointing to the speficied suffix version of QGIS (since the OSGeo install can include no-suffix, `-ltr`, etc. QGIS versions in the same install tree).

- Create a file `<osgeo>/apps/PythonXX/python.pth`, provide access to DLLs in bin with content:

```python
import os; os.add_dll_directory("<osgeo>/bin")
```

- Create a file `<osgeo>/apps/PythonXX/lib/site-packages/pyqt5.pth`, provide access to Qt DLLs with content:

```python
import os; os.add_dll_directory(r"<osgeo>/bin/Qt5/bin")
```

- Create a file `<osgeo>/apps/PythonXX/lib/site-packages/qgis.pth`, provide access to QGIS Python modules and DLLs with content depending on which no-suffix, `-ltr`, etc. of `qgis` directory from `apps` should be used:

```python
<osgeo>/apps/qgis/python
import os; os.add_dll_directory(r"<osgeo>/apps/qgis/bin")
```

- Copy these files in `<osgeo>/bin` also to `<osgeo>/apps/PythonXX/DLLs` directory to make the stdlib usable in venvs without `--system-site-packages` flag:
  - `libcrypto-1_1-x64.dll`
  - `libssl-1_1-x64.dll`
  - `sqlite3.dll`
