# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MappingTools
                                 A QGIS plugin
 Data acquisition tools from vector segmentation layers
                              -------------------
        begin                : 2015-05-05
        git sha              : $Format:%H$
        copyright            : (C) 2015 by IGN
        email                : carhab@ign.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import QgsMapLayerRegistry, QgsMapLayer, QgsVectorLayer, QgsApplication
from qgis.gui import QgisInterface, QgsMapTool

# Initialize Qt resources from file resources.py
import resources_rc

from custom_action import CustomAction
from import_feature import ImportFeature
from fusion import Fusion
#from test_action import TestAction

from common import Common

class MappingTools:

    def __init__(self, iface):
        '''Constructor.
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
        '''Create the menu entries and toolbar icons inside the QGIS GUI.'''

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
            associatedTool=importFeatureMapTool,
            editModeOnly=True,
            checkable=True
            )
        
        fusionMapTool = Fusion(self.iface.mapCanvas())
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
            associatedTool=fusionMapTool,
            editModeOnly=True,
            checkable=True
            )
        
        '''testActionMapTool = TestAction(self.iface.mapCanvas())
        testActionIconPath = self.resourcesPath + 'fusion_icon.png'
        testActionAction = CustomAction(
            iconPath=testActionIconPath,
            text='Test Action',
            enabledFlag=True,
            addToMenu=False,
            addToToolbar=True,
            statusTip=None,
            whatsThis=None,
            parent=self.iface.mainWindow(),
            associatedTool=testActionMapTool,
            mapTool=False,
            editModeOnly=True,
            checkable=False
            )'''
        
        self.addAction(importFeatureAction)
        self.addAction(fusionAction)
        #self.addAction(testActionAction)
        

    def addAction(self, action):
        self.actions.append(action)

        if action.isToAddToToolbar():
            self.toolbar.addAction(action)

        if action.isToAddToMenu():
            self.iface.addPluginToMenu(
                self.menu,
                action)
        #if isinstance(action.getAssociatedTool(), QgsMapTool):
        if action.isMapTool():
            action.getAssociatedTool().setAction(action)
        return action

    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        for action in self.iface.mainWindow().findChild(QToolBar, 'MappingTools').actions():
            self.iface.removePluginMenu(
                'Mapping Tools',
                action)
            self.iface.removeToolBarIcon(action)
