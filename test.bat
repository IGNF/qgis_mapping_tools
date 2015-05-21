set PYTHONPATH="%PYTHONPATH%;C:\OSGeo4W\apps\qgis\python"
set PATH="%PATH;C:\OSGeo4W\bin" # OSGeo4W binaries
set PATH="%PATH;C:\OSGeo4W\apps\qgis\bin" # QGIS binaries


# default QGIS plugins
set PYTHONPATH="%PYTHONPATH%;C:\OSGeo4W\apps\qgis\python\plugins"
# user installed plugins
set PYTHONPATH="%PYTHONPATH%;%USERPROFILE%\.qgis2\python\plugins"

python test/src/testFusion.py
