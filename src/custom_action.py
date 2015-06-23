from PyQt4.QtGui import *
from qgis.utils import iface
from qgis.gui import QgsMapTool

class CustomAction(QAction):
    def __init__(self,
        iconPath,
        text,
        enabledFlag=True,
        addToMenu=True,
        addToToolbar=True,
        statusTip=None,
        whatsThis=None,
        parent=None,
        editModeOnly=True,
        mapTool=None,
        callback=None,
        checkable = True):
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
        super(QAction, self).__init__(QIcon(iconPath), text, parent)
        
        self.addToMenu = addToMenu
        self.addToToolbar = addToToolbar
        self.editModeOnly = editModeOnly
        self.mapTool = mapTool
        self.callback = callback
        
        self.setEnabled(enabledFlag)
        self.setCheckable(checkable)
        
        if statusTip:
            self.setStatusTip(statusTip)

        if whatsThis:
            self.setWhatsThis(whatsThis)
        
        if self.mapTool and not isinstance(self.mapTool, QgsMapTool):
            raise ValueError('mapTool must be QgsMapTool instance')
        
        self.previousActivatedMapTool = None
        
        self.triggered.connect(self.activateAction)
        
        if editModeOnly:
            iface.actionToggleEditing().triggered.connect(self.enableAction)
            iface.mapCanvas().currentLayerChanged.connect(self.manageEnabledStatusAction)
            
    def getMapTool(self):
        return self.mapTool
    
    def getCallback(self):
        return self.callback
    
    def isToAddToMenu(self):
        return self.addToMenu

    def isToAddToToolbar(self):
        return self.addToToolbar

    def isMapTool(self):
        return self.mapTool
        
    def enableAction(self, toEnable):
        self.setEnabled(toEnable)
        
        canvas = iface.mapCanvas()
        if toEnable:
            self.previousActivatedMapTool = canvas.mapTool()
        else:
            canvas.unsetMapTool(self.getMapTool())
            if self.previousActivatedMapTool:
                canvas.setMapTool(self.previousActivatedMapTool)
        
    def manageEnabledStatusAction(self):
        if iface.mapCanvas().currentLayer():
            self.enableAction(iface.mapCanvas().currentLayer().isEditable())
    
    def activateAction(self, activated):
        if self.getMapTool():
            iface.mapCanvas().setMapTool(self.getMapTool())
        if self.getCallback():
            self.getCallback()()
    
            