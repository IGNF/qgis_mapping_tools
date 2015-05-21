from qgis.core import *
from qgis.gui import *

from PyQt4 import QtCore, QtGui, QtTest

import unittest
import os,sys

#sys.path.append("./")

from mapping_tools import MappingTools


class DummyInterface(object):
    def __getattr__(self, *args, **kwargs):
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



class TestFusion(unittest.TestCase):


    def test_fonctionnel(self):
        
        QgsApplication.setPrefixPath("/usr", True)  
        QgsApplication.initQgis()
        
        iface = DummyInterface()
         
        
        QtCore.QCoreApplication.setOrganizationName('QGIS')
        QtCore.QCoreApplication.setApplicationName('QGIS2')
        
        plugin = MappingTools
        
        
        
        #layer = QgsVectorLayer('/home/guillaume/Documents/c++/GIT/qgis_mapping_tools/data/vectors/mailleA-18-C1.shp', 'input', 'ogr')
        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')
        
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
        
    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")

if __name__ == '__main__':
    unittest.main()
    