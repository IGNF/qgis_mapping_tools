from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from PyQt4 import QtCore, QtGui

import unittest

from pymouse import PyMouse
import time
import numpy as np

import MappingTools

class TestMappingTools(unittest.TestCase):

    '''Speed of mouse cursor move, 0.01 =< float =< 1 (0.2 for realistic move)'''
    MOVE_SPEED = 0.2
    
    def __init__(self):
        '''Constructor.
            :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
            :type iface: QgsInterface
        '''
        self.mouse = PyMouse()

    def screenShot(self, imgName = 'debugScreenshot'):
        '''Shoot screen.
            :param imgName: Text value of the action to click on.
            :type imgName: QString
            :default imgName: 'debugScreenshot.png'
        '''
        iface.mapCanvas().saveAsImage(imgName+'.png')
    
    def addTestVectorLayer(self, layerName='test/data/segment.shp'):
        '''Add a vector layer to the map.
            :param layerName: Layer name to add.
            :type layerName: QString
            :default layerName: 'test/data/segement.shp'
        '''

        layer = QgsVectorLayer(layerName, 'input', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def findButtonByActionName(self, buttonActionName):
        '''Find button corresponding to the given action.
            :param buttonActionName: Text value of the action.
            :type buttonActionName: QString
            
            :returns: Widget if found, None else.
            :rtype: QWidget or None
        '''
        for tbar in iface.mainWindow().findChildren(QtGui.QToolBar):
            for action in tbar.actions():
                if action.text() == buttonActionName:
                    for widget in action.associatedWidgets():
                        if type(widget) == QtGui.QToolButton:
                            return widget
        return None

    def mapToScreenPoint(self, mapCoordPoint):
        '''Convert point on the map canvas from map to screen coordinates.
            :param mapCoordPoint: Point in map coordinates.
            :type mapCoordPoint: QgsPoint
            
            :returns: Point in screen coordinates
            :rtype: QPoint
        '''
        # Get point in px into map canvas referential
        sourceScreen = iface.mapCanvas().getCoordinateTransform().transform(mapCoordPoint)
        sourceRelScreen = sourceScreen.toQPointF().toPoint()

        # find top left canvas pos
        canvas = iface.mapCanvas()
        canvasPos = canvas.mapToGlobal(QtCore.QPoint( canvas.rect().x(), canvas.rect().y()))

        # Get point in px into screen referential
        sourceAbsScreen = QtCore.QPoint(sourceRelScreen.x() + canvasPos.x(), sourceRelScreen.y() + canvasPos.y())
        
        return sourceAbsScreen

    def moveTo(self, dest, rate=MOVE_SPEED):
        '''Move smoothly mouse cursor to a destination point.
            :param dest: Mouse cursor destination point.
            :type dest: QPoint

            :param rate: Speed of mouse movement : 1 = 100px/sec.
            :type rate: float >= 0.01
            :default rate: TestMappingTools constant MOVE_SPEED
        '''
        source = self.mouse.position()
        npoints = int(np.sqrt((dest.x()-source[0])**2 + (dest.y()-source[1])**2 ) / (rate*100))
        for i in range(npoints):
            x = int(source[0] + ((dest.x()-source[0])/npoints)*i)
            y = int(source[1] + ((dest.y()-source[1])/npoints)*i)
            self.mouse.move(x,y)
            time.sleep(0.01)

            # Useful to let QGIS processing
            QgsApplication.processEvents()

        self.mouse.move(dest.x(), dest.y())
        
        # Useful to let QGIS processing
        QgsApplication.processEvents()

    def clickOnWidget(self, widget):
        '''Click on the given widget.
            :param widget: Widget to click on.
            :type widget: QWidget
        '''

        widgetX = widget.rect().center().x()
        widgetY = widget.rect().center().y()
        widgetPos = widget.mapToGlobal(QtCore.QPoint(widgetX, widgetY))
       
        self.moveTo(widgetPos)
        self.mouse.click(widgetPos.x(), widgetPos.y(), 1)
        
        # Useful to let QGIS processing
        QgsApplication.processEvents()
        
    def clickOn(self, actionName):
        '''Click on action by its text value.
            :param actionName: Text value of the action to click on.
            :type actionName: QString
        '''
        
        button = self.findButtonByActionName(actionName)
        self.clickOnWidget(button)

    def dragAndDropScreen(self, source, dest):
        '''Press mouse at source point, move to destination point and release.
            :param source: Drag start position.
            :type source: QPoint
            
            :param dest: Mouse cursor destination point.
            :type dest: QPoint
        '''

        self.moveTo(source)
        self.mouse.press(source.x(), source.y(), 1)
        
        # Useful to let QGIS processing
        QgsApplication.processEvents()

        self.moveTo(dest)
        self.mouse.release(dest.x(), dest.y(), 1)
        
        # Useful to let QGIS processing
        QgsApplication.processEvents()

    def dragAndDropMap(self, source, dest):
        '''DragAndDropScreen in map coordinates.
            :param source: Drag start position.
            :type source: QPoint in map coordinates
            
            :param dest: Mouse cursor destination point.
            :type dest: QPoint in map coordinates
        '''
        screenCoordSource = self.mapToScreenPoint(source)
        screenCoordDest = self.mapToScreenPoint(dest)

        self.dragAndDropScreen(screenCoordSource, screenCoordDest)

    def featuresCount(self, layer):
        '''Count the features of a vector layer.
            :param layer: Vector layer.
            :type layer: QgsVectorLayer
            
            :returns: Layer features count.
            :rtype: int
        '''

        count = 0
        for feature in layer.getFeatures():
            count += 1
        return count

    def runFusion(self):
        '''Press mouse at source point, move to destination point and release.
            :returns: The layer after processing.
            :rtype: QgsVectorLayer
        '''

        # Open python console
        iface.actionShowPythonDialog().trigger()
        #Add test layer to map registry
        self.addTestVectorLayer()
        # Set layer in edit mode
        self.clickOn(iface.actionToggleEditing().text())
        # Activate fusion action
        self.clickOn('Fusion')
        # Press and move on the map canvas to carry out the fusion
        self.dragAndDropMap(QgsPoint(783902,6528458),  QgsPoint(785223,6528279))
        
        return iface.mapCanvas().layers()[0]
    
    def testFusion(self):
        
        layerResult = self.runFusion()
        # Compare the features count with the expected result 
        featuresCount = self.featuresCount(layerResult)
        if featuresCount == 35:
            print 'Fusion OK'
        else:
            print 'Fusion test fails'
            return
    def testImportFeature(self):
        pass

TestMappingTools().testFusion()
TestMappingTools().testImportFeature()