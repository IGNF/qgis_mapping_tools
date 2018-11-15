from __future__ import print_function


from builtins import object
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import QtCore, QtGui

import unittest
import os,sys

# sys.path.append("./")
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
        return list(QgsProject.instance().mapLayers().values())
    def mapCanvas(self):
        return self.canvas



class TestFusion(unittest.TestCase):


    def test_fonctionnel(self):

        prefix_path = os.environ['QGIS_PREFIX_PATH']
        # fix_print_with_import
        print("Env QGIS_PREFIX_PATH : {}".format(prefix_path))
        QgsApplication.setPrefixPath(prefix_path, True)
        QgsApplication.initQgis()
        app = QgsApplication([], True)


        QtCore.QCoreApplication.setOrganizationName('QGIS')
        QtCore.QCoreApplication.setApplicationName('QGIS2')

        plugin = MappingTools



        layer = QgsVectorLayer('test/data/segment.shp', 'input', 'ogr')

        canvas = QgsMapCanvas()
        canvas.fullExtent()
        iface = DummyInterface(canvas)
        if not layer.isValid():

            # fix_print_with_import
            print("Probleme de chargement du shapefile...")
            # fix_print_with_import
            print("- Verifiez la liste des provider (need OGR) :")
            providers = QgsProviderRegistry.instance().providerList()
            for provider in providers:
                # fix_print_with_import
                print(provider)
            # fix_print_with_import
            print("- Verifiez la liste des chemins :")
            # fix_print_with_import
            print(QgsApplication.showSettings())
            self.fail('Failed to load "{} - ".'.format(layer.source()))


        QgsProject.instance().addMapLayer(layer)

        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()


        # fix_print_with_import
        print(layer.dataProvider().featureCount())
        # fix_print_with_import
        print(total_area)
        self.plugin = MappingTools.classFactory(iface)
        #self.plugin = Common()
        # fix_print_with_import
        print(canvas.mapSettings().outputSize())
        # fix_print_with_import
        print(canvas.mapSettings().extent())
        self.assertEqual(self.plugin.common.screenCoordsToMapPoint(658,-478), (783810,6528060))

    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")

if __name__ == '__main__':
    unittest.main()
