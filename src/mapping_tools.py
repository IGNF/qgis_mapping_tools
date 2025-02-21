# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MappingTools Class

        A QGIS plugin Data acquisition tools from vector segmentation layers

        begin : 2015-05-05

        author : IGN

        contact : carhab@ign.fr
 ***************************************************************************/

"""
from __future__ import absolute_import

from builtins import object
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QToolBar

from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer, QgsApplication
from qgis.gui import QgisInterface, QgsMapTool, QgsMapToolZoom

# Initialize Qt resources from file resources.py
from .resources import *

from .custom_action import CustomAction
from .import_feature import ImportFeature
from .fusion import Fusion

from .custom_maptool import CustomMapTool

class MappingTools(object):

    def __init__(self, iface):
        '''
        Constructor.

        :param iface: An interface instance that will be passed to this class
        which provides the hook by which you can manipulate the QGIS
        application at run time.
        :type iface: QgsInterface
        '''
        # Save reference to the QGIS interface
        self.iface = iface
        # Declare instance attributes
        self.actions = []
        self.menu = 'Mapping Tools'
        self.toolbar = self.iface.addToolBar(u'MappingTools')
        self.toolbar.setObjectName(u'MappingTools')
        self.resourcesPath = ':/plugins/MappingTools/resources/img/'

    def initGui(self):
        '''Instanciate CustomActions to add to plugin toolbar.'''

        # Import feature action instance.
        importFeatureMapTool = ImportFeature(self.iface)
        importFeatureIconPath = self.resourcesPath + 'import_feature_icon.png'
        importFeatureAction = CustomAction(
            iconPath=importFeatureIconPath,
            text='Import Feature',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            mapTool=importFeatureMapTool,
            editModeOnly=True,
            checkable=True
            )

        # Fusion action instance.
        fusionMapTool = Fusion(self.iface)
        fusionIconPath = self.resourcesPath + 'fusion_icon.png'
        fusionAction = CustomAction(
            iconPath=fusionIconPath,
            text='Fusion',
            enabledFlag=False,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            mapTool=fusionMapTool,
            editModeOnly=True,
            checkable=True
            )

        # Add created actions to plugin.
        self.addAction(importFeatureAction)
        self.addAction(fusionAction)

    def addAction(self, action):
        '''
        Add custom actions to toolbar, menu and bind its to map tool if defined.

        :param action: A custom action instance.
        :type action: CustomAction
        '''

        self.actions.append(action)

        if action.isToAddToToolbar():
            self.toolbar.addAction(action)

        if action.isToAddToMenu():
            self.iface.addPluginToMenu(
                self.menu,
                action)

        if action.getMapTool():
            action.getMapTool().setAction(action)

    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''

        for action in self.iface.mainWindow().findChild(QToolBar, 'MappingTools').actions():
            self.iface.removePluginMenu(
                'Mapping Tools',
                action)
            self.iface.removeToolBarIcon(action)
