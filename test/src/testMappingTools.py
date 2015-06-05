from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from PyQt4 import QtCore, QtGui

from pymouse import PyMouse
from pykeyboard import PyKeyboard

import time
import numpy as np

import MappingTools

class TestMappingTools(object):

    '''Speed of mouse cursor move, 0.01 =< float =< 1 (0.2 for realistic move)'''
    MOVE_SPEED = 0.2
    # Do full test or a part only
    TESTS_TO_CHECK = '' # available values : 'up_to_fusion', 'up_to_undo', 'up_to_quit_edit' , every thing else for full test
    
    def __init__(self):
        '''Constructor.
            :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
            :type iface: QgsInterface
        '''
        self.mouse = PyMouse()
        self.keyboard = PyKeyboard()

    def screenShot(self, imgName = 'debugScreenshot'):
        '''Shoot screen.
            :param imgName: Text value of the action to click on.
            :type imgName: QString
            :default imgName: 'debugScreenshot.png'
        '''
        
        iface.mapCanvas().saveAsImage(imgName)
    
    def addTestVectorLayer(self, layerName='test/data/segment.shp'):
        '''Add a vector layer to the map.
            :param layerName: Layer name to add.
            :type layerName: QString
            :default layerName: 'test/data/segement.shp'
            
            :returns: Vector layer which has been added to map canvas
            :rtype: QgsVectorLayer
        '''

        layer = QgsVectorLayer(layerName, 'input', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        # Useful to let QGIS processing
        QgsApplication.processEvents()
        return iface.mapCanvas().layers()[0]

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
    
    def ctrlZ(self):
        '''Simulates 'CTRL + z' type on the keyboard.'''
        
        self.keyboard.press_key(self.keyboard.control_l_key)
        time.sleep(0.25)
        self.keyboard.tap_key(self.keyboard.type_string('z'), 0, 0)
        time.sleep(0.25)
        self.keyboard.release_key(self.keyboard.control_l_key)
        # Useful to let QGIS processing
        QgsApplication.processEvents()
    
    def quitLayerEditMode(self, layer):
        '''Rollback changes on the layer and quit edit mode.
            :param layer: Layer in edit mode.
            :type layer: QVectorLayer
        '''
        
        layer.rollBack()
        # Useful to let QGIS processing
        QgsApplication.processEvents()
        # Refresh layer layout
        layer.triggerRepaint()
    
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
    
    def printTest(self, expected, result, testName, valueToTestName):
        '''Print test result.
            :param expected: expected value to test.
            :type expected: unknown
			
            :param result: result value to test.
            :type result: unknown
			
            :param testName: Name of test (into header printed).
            :type testName: QString
            
			:param valueToTestName: Tested variable name (printed if test fails).
            :type valueToTestName: QString
            
            :returns: True if test pass, False else.
            :rtype: Bool
        '''

        test = False
        msg = testName+''' : Fails
                '''+valueToTestName+''' expected : '''+str(expected)+'''
                '''+valueToTestName+''' : '''+str(result)
        if expected == result:
            test = True
            msg = testName+''' : OK'''
        print msg
        return test
    
    def testFusion(self):
        '''Simulate user moves and check results.'''

        # Open python console
        iface.actionShowPythonDialog().trigger()
        # Get map tool action that is activated
        previousActivatedMapToolActionName = iface.mapCanvas().mapTool().action().text()
        #Add test layer to map registry
        layer = self.addTestVectorLayer()

        # Simulate click on edit mode button
        self.clickOn(iface.actionToggleEditing().text())

        # Simulate click on plugin fusion button
        self.clickOn('Fusion')

        # Press (left click) and move mouse on the map canvas to carry out the fusion
        self.dragAndDropMap(QgsPoint(783902,6528458),  QgsPoint(785223,6528279))

        # Features must have been merged (test with features count)
        if not self.printTest(35, self.featuresCount(layer), 'Fusion', 'Features count'):
            return
        
        # End of test ?
        if self.TESTS_TO_CHECK == 'up_to_fusion':
            return
        
        # Test undo action
        self.ctrlZ() 
        if not self.printTest(37, self.featuresCount(layer), 'Undo (Ctrl + z)', 'Features count'):
            return
        
        # End of test ?
        if self.TESTS_TO_CHECK == 'up_to_undo':
            return
        
        # Quit edit mode
        self.quitLayerEditMode(layer)
        
        # Fusion button must be enabled
        if not self.printTest(False, self.findButtonByActionName('Fusion').isEnabled(), 'Disable fusion button', 'Fusion button status'):
            return
        
        # Previous map tool button must be re-checked
        if not self.printTest(True, self.findButtonByActionName(previousActivatedMapToolActionName).isChecked(), 'Check previous map tool button ('+previousActivatedMapToolActionName+')', 'Previous map tool button ('+previousActivatedMapToolActionName+') status'):
            return
        
        # End of test ?
        if self.TESTS_TO_CHECK == 'up_to_quit_edit':
            return

    def testImportFeature(self):
        pass

TestMappingTools().testFusion()
TestMappingTools().testImportFeature()