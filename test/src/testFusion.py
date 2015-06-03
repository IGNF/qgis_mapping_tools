from qgis.core import *
from qgis.gui import *
from qgis.utils import iface

from PyQt4 import QtCore, QtGui, uic

from pymouse import PyMouse
import unittest

import MappingTools
from common import Common
from PyQt4.Qt import QObject

class TestFusion(unittest.TestCase):

    def test_fonctionnel(self):

        iface.actionShowPythonDialog().trigger()
        prefix_path = os.environ['QGIS_PREFIX_PATH']
        print "Env QGIS_PREFIX_PATH : {}".format(prefix_path)
        QgsApplication.setPrefixPath(prefix_path, True)  
        QgsApplication.initQgis()
        QtCore.QCoreApplication.setOrganizationName('QGIS')
        QtCore.QCoreApplication.setApplicationName('QGIS2')

        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer.startEditing()
        
        #iface.mapCanvas().saveAsImage('img.png')
        
        pluginTbar = iface.mainWindow().findChild(QtGui.QToolBar, "MappingTools")
        for action in pluginTbar.actions():
            if action.text() == 'Fusion':
                fusionAction = action
        
        for wdgt in fusionAction.associatedWidgets():
            if type(wdgt) == QtGui.QToolButton:
                fusionBtn = wdgt
        
        fusionBtnX = fusionBtn.rect().center().x()
        fusionBtnY = fusionBtn.rect().center().y()
        fusionBtnPos = fusionBtn.mapToGlobal(QtCore.QPoint(fusionBtnX, fusionBtnY))
        m = PyMouse()
        m.click(fusionBtnPos.x(), fusionBtnPos.y())
        
        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()

        print layer.dataProvider().featureCount()
        print total_area

    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")
TestFusion("test_fonctionnel").test_fonctionnel()

#if __name__ == '__main__':
#    unittest.main()
