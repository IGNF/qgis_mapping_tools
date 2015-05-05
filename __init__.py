# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MappingTools
                                 A QGIS plugin
 Data acquisition tools from vector segmentation layers
                             -------------------
        begin                : 2015-05-05
        copyright            : (C) 2015 by IGN
        email                : carhab@ign.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MappingTools class from file MappingTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .mapping_tools import MappingTools
    return MappingTools(iface)
