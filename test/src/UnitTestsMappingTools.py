

from qgis.core import *
from qgis.gui import *
from PyQt4 import QtCore, QtGui, QtTest

import unittest
import os,sys

#sys.path.append("./")
import MappingTools
from common import Common


class DummyInterface(object):
    def __init__(self, canvas):
        self.canvas = canvas
    def __getattr__(self, canvas, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration
    def layers(self):
        # simulate iface.legendInterface().layers()
        return QgsMapLayerRegistry.instance().mapLayers().values()
    def mapCanvas(self):
        return self.canvas



class TestFusion(unittest.TestCase):


    def test_fonctionnel(self):
        
        prefix_path = os.environ['QGIS_PREFIX_PATH']
        print "Env QGIS_PREFIX_PATH : {}".format(prefix_path)
        QgsApplication.setPrefixPath(prefix_path, True)  
        QgsApplication.initQgis()
        app = QgsApplication([], True)
         
        
        QtCore.QCoreApplication.setOrganizationName('QGIS')
        QtCore.QCoreApplication.setApplicationName('QGIS2')
        
        plugin = MappingTools
        
        
        
        #layer = QgsVectorLayer('/home/guillaume/Documents/c++/GIT/qgis_mapping_tools/data/vectors/mailleA-18-C1.shp', 'input', 'ogr')
        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')
        
        canvas = QgsMapCanvas()
        canvas.fullExtent()
        iface = DummyInterface(canvas)
        if not layer.isValid():
            
            print "Probleme de chargement du shapefile..."
            print "- Verifiez la liste des provider (need OGR) :"
            providers = QgsProviderRegistry.instance().providerList()
            for provider in providers:
                print provider
            print "- Verifiez la liste des chemins :"
            print QgsApplication.showSettings()
            self.fail('Failed to load "{} - ".'.format(layer.source()))
        
        
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        
        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()

        
        print layer.dataProvider().featureCount()
        print total_area
        self.plugin = MappingTools.classFactory(iface)
        #self.plugin = Common()
        print canvas.mapSettings().outputSize()
        print canvas.mapSettings().extent()
        self.assertEqual(self.plugin.common.screenCoordsToMapPoint(658,-478), (783810,6528060))
        
    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")

if __name__ == '__main__':
    unittest.main()
    

