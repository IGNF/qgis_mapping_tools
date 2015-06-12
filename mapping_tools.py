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
from PyQt4 import QtGui

from qgis.core import QgsMapLayerRegistry, QgsMapLayer, QgsVectorLayer, QgsApplication

# Initialize Qt resources from file resources.py
import resources_rc

from import_feature import ImportFeature
from fusion import Fusion


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
        self.mapTools = {}
        self.menu = 'Mapping Tools'
        self.toolbar = self.iface.addToolBar(u'MappingTools')
        self.toolbar.setObjectName(u'MappingTools')
        self.previousActivatedMapTool = None
        self.enableFusionAction = None
        self.disableFusionAction = None
        self.enableImportFeatAction = None
        self.disableImportFeatAction = None

    def add_action(
        self,
        id,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        mapTool=None):
        '''Add a toolbar icon to the toolbar.
            :param icon_path: Path to the icon for this action. Can be a resource
                path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
            :type icon_path: str

            :param text: Text that should be shown in menu items for this action.
            :type text: str

            :param callback: Function to be called when the action is triggered.
            :type callback: function

            :param enabled_flag: A flag indicating if the action should be enabled
                by default. Defaults to True.
            :type enabled_flag: bool

            :param add_to_menu: Flag indicating whether the action should also
                be added to the menu. Defaults to True.
            :type add_to_menu: bool

            :param add_to_toolbar: Flag indicating whether the action should also
                be added to the toolbar. Defaults to True.
            :type add_to_toolbar: bool

            :param status_tip: Optional text to show in a popup when mouse pointer
                hovers over the action.
            :type status_tip: str

            :param parent: Parent widget for the new action. Defaults None.
            :type parent: QWidget

            :param whats_this: Optional text to show in the status bar when the
                mouse pointer hovers over the action.

            :returns: The action that was created. 
            :rtype: QAction
        '''
        icon = QtGui.QIcon(icon_path)
        action = QtGui.QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
            
        if mapTool:
            mapTool.setAction(action)
        self.mapTools[action] = mapTool

        return action

    def initGui(self):

        '''Create the menu entries and toolbar icons inside the QGIS GUI.'''
        
        importFeatureMapTool = ImportFeature(self.iface)
        import_feature_icon_path = ':/plugins/MappingTools/import_feature_icon.png'
        import_feature_action = self.add_action(
            'import_feature_action',
            import_feature_icon_path,
            text='Import Feature',
            callback=self.importFeature,
            enabled_flag=False,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
            mapTool=importFeatureMapTool)
        
        fusionMapTool = Fusion(self.iface.mapCanvas())
        fusion_icon_path = ':/plugins/MappingTools/fusion_icon.png'
        fusion_action = self.add_action(
            'fusion_action',
            fusion_icon_path,
            text='Fusion',
            callback=self.fusion,
            enabled_flag=False,
            add_to_menu=False,
            parent=self.iface.mainWindow(),
            mapTool=fusionMapTool)
        for action in self.iface.mainWindow().findChild(QtGui.QToolBar, 'MappingTools').actions():
            self.setMapToolBehaviour(action)
        self.manageButtonBehaviour()
        #self.clyr = self.iface.mapCanvas().currentLayer()
        #self.manageButtonBehaviourWithCurLyr = lambda: self.manageButtonBehaviour(self.clyr)
        #self.iface.mapCanvas().currentLayerChanged.connect(self.manageButtonBehaviourWithCurLyr)
        self.iface.mapCanvas().currentLayerChanged.connect(self.manageButtonBehaviour)
    
    def findActionByName(self, actionName):
        for tbar in self.iface.mainWindow().findChildren(QtGui.QToolBar):
            for action in tbar.actions():
                if action.text() == actionName:
                    return action
        return None
    
    def setMapToolBehaviour(self, action):
        action.setCheckable(True)
        
    def unload(self):
        #self.iface.mapCanvas().currentLayerChanged.disconnect(self.manageButtonBehaviourWithCurLyr)
        '''if self.enableFusionAction:
            self.iface.mapCanvas().currentLayer().editingStarted.disconnect(self.enableFusionAction)
        if self.disableFusionAction:
            self.iface.mapCanvas().currentLayer().editingStopped.disconnect(self.disableFusionAction)
        if self.enableImportFeatAction:
            self.iface.mapCanvas().currentLayer().editingStarted.disconnect(self.enableImportFeatAction)
        if self.disableImportFeatAction:
            self.iface.mapCanvas().currentLayer().editingStopped.disconnect(self.disableImportFeatAction)'''
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        for action in self.iface.mainWindow().findChild(QtGui.QToolBar, 'MappingTools').actions():
            self.iface.removePluginMenu(
                'Mapping Tools',
                action)
            self.iface.removeToolBarIcon(action)
            # Unset the map tool in case it's set
            self.iface.mapCanvas().unsetMapTool(self.mapTools[action])
        
        # Useful to let QGIS processing
        QgsApplication.processEvents()
            
    def importFeature(self):
        if self.iface.mapCanvas().mapTool().action() not in self.iface.mainWindow().findChild(QtGui.QToolBar, 'MappingTools').actions():
            self.previousActivatedMapTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTools[self.findActionByName('Import Feature')])

    def fusion(self):
        if self.iface.mapCanvas().mapTool().action() not in self.iface.mainWindow().findChild(QtGui.QToolBar, 'MappingTools').actions():
            self.previousActivatedMapTool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.mapTools[self.findActionByName('Fusion')])
        
        
    def manageButtonBehaviour(self):
        '''if previousCurrentlayer:
            if self.enableFusionAction:
                previousCurrentlayer.editingStarted.disconnect(self.enableFusionAction)
            if self.disableFusionAction:
                previousCurrentlayer.editingStopped.disconnect(self.disableFusionAction)
            if self.enableImportFeatAction:
                previousCurrentlayer.editingStarted.disconnect(self.enableImportFeatAction)
            if self.disableImportFeatAction:
                previousCurrentlayer.editingStopped.disconnect(self.disableImportFeatAction)'''
        currentLayer = self.iface.mapCanvas().currentLayer()
        #self.clyr = currentLayer
        if not currentLayer:
            return
        if currentLayer.isEditable():
            self.enableAction()
        else:
            self.disableAction()
        
        if type(currentLayer) == QgsVectorLayer:
            '''self.enableFusionAction = lambda: self.enableAction(self.findActionByName('Fusion'))
            self.disableFusionAction = lambda: self.disableAction(self.findActionByName('Fusion'))
            self.enableImportFeatAction = lambda: self.enableAction(self.findActionByName('Import Feature'))
            self.disableImportFeatAction = lambda: self.disableAction(self.findActionByName('Import Feature'))
            currentLayer.editingStarted.connect(self.enableFusionAction)
            currentLayer.editingStopped.connect(self.disableFusionAction)
            currentLayer.editingStarted.connect(self.enableImportFeatAction)
            currentLayer.editingStopped.connect(self.disableImportFeatAction)'''
            currentLayer.editingStarted.connect(self.enableAction)
            currentLayer.editingStopped.connect(self.disableAction)
        
    def enableAction(self):
        self.findActionByName('Import Feature').setEnabled(True)
        self.findActionByName('Fusion').setEnabled(True)
        
    def disableAction(self):
        self.findActionByName('Import Feature').setDisabled(True)
        self.findActionByName('Fusion').setDisabled(True)
        self.iface.mapCanvas().unsetMapTool(self.mapTools[self.findActionByName('Fusion')])
        self.iface.mapCanvas().unsetMapTool(self.mapTools[self.findActionByName('Import Feature')])
        if not self.previousActivatedMapTool == None:
            self.iface.mapCanvas().setMapTool(self.previousActivatedMapTool)
