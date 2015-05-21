#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:/usr/share/qgis/python"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/lib/qgis/plugins/"

# default QGIS plugins
export PYTHONPATH="${PYTHONPATH}:/usr/share/qgis/python/plugins"
# user installed plugins
export PYTHONPATH="${PYTHONPATH}:${HOME}/.qgis2/python/plugins"


export QGIS_DEBUG="1"

python test/src/testFusion.py

