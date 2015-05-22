set PYTHONPATH=%PYTHONPATH%;C:\OSGeo4W\apps\qgis\python
set PATH=%PATH%;C:\OSGeo4W\bin
set PATH=%PATH%;C:\OSGeo4W\apps\qgis\bin
set PYTHONPATH=%PYTHONPATH%;C:\OSGeo4W\apps\qgis\python\plugins
set PYTHONPATH=%PYTHONPATH%;%USERPROFILE%\.qgis2\python\plugins
set PYTHONPATH=%PYTHONPATH%;./
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis

python test\src\testFusion.py