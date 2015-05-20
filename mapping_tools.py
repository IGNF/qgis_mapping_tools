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
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsMapLayerRegistry, QgsMapLayer

# Initialize Qt resources from file resources.py
import resources_rc
from import_feature import ImportFeature
from fusion import Fusion
import os.path


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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # Declare instance attributes
        self.actions = []
        self.menu = 'Mapping Tools'
        self.toolbar = self.iface.addToolBar(u'MappingTools')
        self.toolbar.setObjectName(u'MappingTools')
        
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
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

            :returns: The action that was created. Note that the action is also
                added to self.actions list.
            :rtype: QAction
        '''

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
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

        self.actions.append(action)

        return action

    def initGui(self):
        '''Create the menu entries and toolbar icons inside the QGIS GUI.'''
        import_feature_icon_path = ':/plugins/MappingTools/import_feature_icon.png'
        import_feature_action = self.add_action(
            import_feature_icon_path,
            text='Import Feature',
            callback=self.importFeature,
            add_to_menu=False,
            parent=self.iface.mainWindow())
        
        self.fusionMapTool = Fusion(self.iface.mapCanvas())
        fusion_icon_path = ':/plugins/MappingTools/fusion_icon.png'
        fusion_action = self.add_action(
            fusion_icon_path,
            text='Fusion',
            callback=self.fusion,
            enabled_flag=False,
            add_to_menu=False,
            parent=self.iface.mainWindow())
        fusion_action.setCheckable(True)
        self.fusionMapTool.setAction(fusion_action)
        self.fusionMapTool.activated.connect(self.keepPressed)
        self.fusionMapTool.deactivated.connect(self.unCheck)
        
        self.layerChangedEvent(self.iface.mapCanvas().currentLayer())
        self.iface.mapCanvas().currentLayerChanged.connect(self.layerChangedEvent)

    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        for action in self.actions:
            self.iface.removePluginMenu(
                'Mapping Tools',
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        # Unset the map tool in case it's set
        self.iface.mapCanvas().unsetMapTool(self.fusionMapTool)

    def keepPressed(self):
        self.actions[1].setChecked(True)

    def unCheck(self):
        self.actions[1].setChecked(False)

    def importFeature(self):
        ImportFeature(self.iface, sourceLayer= '', destinationLayer='')

    def fusion(self):
        self.iface.mapCanvas().setMapTool(self.fusionMapTool)
        
    def layerChangedEvent(self, currentLayer):
        if not currentLayer:
            return
        if currentLayer.isEditable():
            self.actions[1].setEnabled(True)
        else:
            self.actions[1].setEnabled(False)
            self.iface.mapCanvas().unsetMapTool(self.fusionMapTool)
        currentLayer.editingStarted.connect(self.editingStartedEvent)
        currentLayer.editingStopped.connect(self.editingStoppedEvent)
        
    def editingStartedEvent(self):
        self.actions[1].setEnabled(True)
        
    def editingStoppedEvent(self):
        self.actions[1].setEnabled(False)
        self.iface.mapCanvas().unsetMapTool(self.fusionMapTool)