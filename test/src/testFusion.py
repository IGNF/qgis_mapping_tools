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
        
        # find top left canvas pos
        canvas = iface.mapCanvas()
        canvasX = canvas.rect().x()
        canvasY = canvas.rect().y()
        self.canvasPos = canvas.mapToGlobal(QtCore.QPoint(canvasX, canvasY))
        
    def screenShot(self):
        iface.mapCanvas().saveAsImage('debugScreenshot.png')
        
    def findButtonByActionName(self, buttonActionName):
        for tb in iface.mainWindow().findChildren(QtGui.QToolBar):
            for action in tb.actions():
                if action.text() == buttonActionName:
                    for wdgt in action.associatedWidgets():
                        if type(wdgt) == QtGui.QToolButton:
                            return wdgt
        return None
    
    def clickOnWidget(self, widget):
        
        fusionBtnX = widget.rect().center().x()
        fusionBtnY = widget.rect().center().y()
        fusionBtnPos = widget.mapToGlobal(QtCore.QPoint(fusionBtnX, fusionBtnY))
       
        self.moveTo(fusionBtnPos)
        
        self.mouse.click(fusionBtnPos.x(), fusionBtnPos.y(), 1)
    
    def convertFieldPointToScreenPoint(self, fieldPoint):
        trsfObj = iface.mapCanvas().getCoordinateTransform()
        sourceScreen = trsfObj.transform(fieldPoint)
        sourceRelScreen = sourceScreen.toQPointF().toPoint()
        sourceAbsScreen = QtCore.QPoint(sourceRelScreen.x() + self.canvasPos.x(), sourceRelScreen.y() + self.canvasPos.y())
        return sourceAbsScreen
    
    def test_fonctionnel(self):
        
        
        iface.actionShowPythonDialog().trigger()
        
        
        

        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')
        
        
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        
        
        
        self.clickOnWidget(self.findButtonByActionName(iface.actionToggleEditing().text()))
        
        
        
        fusionBtn = self.findButtonByActionName('Fusion')
        self.clickOnWidget(fusionBtn)
        

        sourceTerrain = QgsPoint(783902,6528458)
        source = self.convertFieldPointToScreenPoint(sourceTerrain)
        destTerrain = QgsPoint(785223,6528279)
        dest = self.convertFieldPointToScreenPoint(destTerrain)

        self.dragAndDrop(source, dest)

        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()
    
    def moveTo(self, dest, rate=5):
        # smooth move from source to dest
        source = self.mouse.position()
        npoints = int(np.sqrt((dest.x()-source[0])**2 + (dest.y()-source[1])**2 ) / rate)
        for i in range(npoints):
            x = int(source[0] + ((dest.x()-source[0])/npoints)*i)
            y = int(source[1] + ((dest.y()-source[1])/npoints)*i)
            self.mouse.move(x,y)
            time.sleep(0.01)
        
        self.mouse.move(dest.x(),dest.y())
    
    def dragAndDrop(self, source, dest, rate=5):
        
        self.moveTo(source)
        self.mouse.press(source.x(), source.y(), 1)
        
        self.moveTo(dest, rate)
        self.mouse.release(dest.x(), dest.y(), 1)
    
    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")
TestFusion().test_fonctionnel()

#if __name__ == '__main__':
#    unittest.main()
