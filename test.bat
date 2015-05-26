call c:\OSGeo4W\bin\o4w_env.bat
set PYTHONPATH=C:\OSGeo4W\apps\qgis\python;%PYTHONPATH%
set PATH=C:\OSGeo4W\bin;%PATH%
set PATH=C:\OSGeo4W\apps\qgis\bin;%PATH%
set PYTHONPATH=C:\OSGeo4W\apps\qgis\python\plugins;%PYTHONPATH%
set PYTHONPATH=%USERPROFILE%\.qgis2\python\plugins;%PYTHONPATH%
set PYTHONPATH=./;%PYTHONPATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis

python test\src\testFusion.py