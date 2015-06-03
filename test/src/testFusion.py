from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import threading
from PyQt4 import QtCore, QtGui, uic

from pymouse import PyMouse
import time
import unittest
import numpy as np
import MappingTools
from common import Common
from PyQt4.Qt import QObject

class TestFusion(unittest.TestCase):

    def __init__(self):
        
        self.mouse = PyMouse()
        self.pluginTbar = iface.mainWindow().findChild(QtGui.QToolBar, "MappingTools")
        
        # find top left canvas pos
        canvas = iface.mapCanvas()
        canvasX = canvas.rect().x()
        canvasY = canvas.rect().y()
        self.canvasPos = canvas.mapToGlobal(QtCore.QPoint(canvasX, canvasY))
        
    def screenShot(self):
        iface.mapCanvas().saveAsImage('debugScreenshot.png')
        
    def findButtonByActionName(self, buttonActionName):
        for action in self.pluginTbar.actions():
            if action.text() == buttonActionName:
                fusionAction = action
        for wdgt in fusionAction.associatedWidgets():
            if type(wdgt) == QtGui.QToolButton:
                return wdgt
        return None
    
    def clickOnWidget(self, widget):
        
        fusionBtnX = widget.rect().center().x()
        fusionBtnY = widget.rect().center().y()
        fusionBtnPos = widget.mapToGlobal(QtCore.QPoint(fusionBtnX, fusionBtnY))
       
        self.mouse.click(fusionBtnPos.x(), fusionBtnPos.y())
    
    def convertFieldPointToScreenPoint(self, fieldPoint):
        trsfObj = iface.mapCanvas().getCoordinateTransform()
        print trsfObj
        sourceScreen = trsfObj.transform(fieldPoint)
        
        print "Source screen float : " + str(sourceScreen)
        
        sourceRelScreen = sourceScreen.toQPointF().toPoint()
        sourceAbsScreen = QtCore.QPoint(sourceRelScreen.x() + self.canvasPos.x(), sourceRelScreen.y() + self.canvasPos.y())
        return sourceAbsScreen
    
    def test_fonctionnel(self):
        iface.actionShowPythonDialog().trigger()
        
        

        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')
        
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        
        #print ''
        
        layer.startEditing()
        
        
        fusionBtn = self.findButtonByActionName('Fusion')
        self.clickOnWidget(fusionBtn)
        #time.sleep(1)

        sourceTerrain = QgsPoint(783902,6528458)
        source = self.convertFieldPointToScreenPoint(sourceTerrain)
        destTerrain = QgsPoint(785223,6528279)
        dest = self.convertFieldPointToScreenPoint(destTerrain)

        self.testDragAndDrop(source, dest, 2000)

        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()

        print layer.dataProvider().featureCount()
        print total_area
        
    def testDragAndDrop(self, source, dest, rate=1000):
        
        
        print "source screen int " + str(source)
        
        print "canvas pos : " + str(self.canvasPos)
        
        self.mouse.press(source.x(), source.y(), 1)
        # smooth move from source to dest
        npoints = int(np.sqrt((dest.x()-source.x())**2 + (dest.y()-source.y())**2 ) / (rate/1000))
        for i in range(npoints):
            x = int(source.x() + ((dest.x()-source.x())/npoints)*i)
            y = int(source.y() + ((dest.y()-source.y())/npoints)*i)
            self.mouse.move(x,y)
            time.sleep(0.001)
    
        self.mouse.release(dest.x(), dest.y())
        print "final : " + str(source.x()) + " - " + str(source.y())
        #print source
        
        
        """
        desta = QgsPoint(785223.95104895125,6528279.0209790133)
        destb = iface.mapCanvas().getCoordinateTransform().transform(desta)
        dest = destb.toQPointF().toPoint()
        
        print source
        print dest
        rate=1000
        self.mouse.press(source.x(),source.y())
        # smooth move from source to dest
        npoints = int(np.sqrt((dest.x()-source.x())**2 + (dest.y()-source.y())**2 ) / (rate/1000))
        for i in range(npoints):
            x = int(source.x() + ((dest.x()-source.x())/npoints)*i)
            y = int(source.y() + ((dest.y()-source.y())/npoints)*i)
            self.mouse.move(x,y)
            time.sleep(0.001)
    
        self.mouse.release(dest.x(), dest.y())
        """
    
    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")
TestFusion().test_fonctionnel()

#if __name__ == '__main__':
#    unittest.main()
