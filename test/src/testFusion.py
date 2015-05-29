from qgis.core import *
from qgis.gui import *
from PyQt4 import QtCore, QtGui, uic

import unittest
import os,sys
from qgis_interface import QgisInterface
#sys.path.append("./")

import MappingTools
from common import Common
from PyQt4.Qt import QObject, QTest

class DummyCanvas(object):
    def __getattr__(self, *args, **kwargs):
        def dummy(*args, **kwargs):
            return self
        return dummy
    
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
    def mainWindow(self):
        return None
    def mapCanvas(self):
        return QgsMapCanvas()
    
class SignalBox(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.received = {}
    def __getattr__(self, key):
        return partial(self.__slot, key)
    def __slot(self, attr=None, *args):
        sig = tuple([self.sender()] + list(args))
        if attr not in self.received:
            self.received[attr] = []
        self.received[attr].append(sig)

class TestFusion(unittest.TestCase):

    message_log = {}
    
    def log(self, message, tag, level):
        self.message_log.setdefault(tag, [])
        self.message_log[tag].append((message, level,))
       


    def test_fonctionnel(self):
        
        QgsMessageLog.instance().messageReceived.connect(self.log)
        
        prefix_path = os.environ['QGIS_PREFIX_PATH']
        print "Env QGIS_PREFIX_PATH : {}".format(prefix_path)
        app = QtGui.QApplication(sys.argv)
        QgsApplication.setPrefixPath(prefix_path, True)  
        QgsApplication.initQgis()
        #print app
        # Get an iface object
        canvas = QgsMapCanvas()
        iface = QgisInterface(canvas)

        QgsMapLayerRegistry.instance().addMapLayer(iface.activeLayer())
        iface.mapCanvas().setCurrentLayer(iface.activeLayer())
        clayer = iface.mapCanvas().currentLayer()
        print clayer
        
        QtCore.QCoreApplication.setOrganizationName('QGIS')
        QtCore.QCoreApplication.setApplicationName('QGIS2')

        self.plugin = MappingTools.classFactory(iface)
        #self.ui = self.plugin.dlg.ui # useful for shorthand later
        self.plugin.initGui()
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
        clayer.startEditing()
        print clayer.isEditable()
        iface.mapCanvas().saveAsImage('img.png')
        #signalbox = SignalBox()
        #iface.mapCanvas().
        #cursor = QtGui.QCursor()
        #iface.mapCanvas().setCursor(cursor)
        #pos = cursor.pos()
        #cursor.setPos(pos.x()+1, pos.y()+1)
        #print cursor
        #event = QtGui.QMouseEvent(2, QtCore.QPoint(), 1, 0, 0)
        #qpoint = iface.mapCanvas().getCoordinateTransform().transform(784096.41,6528576.19).toQPointF().toPoint()
        qpoint = QtCore.QPoint()
        print isinstance(iface.mapCanvas(), QtGui.QWidget)
        
        QgsMessageLog.instance().logMessage("TEST MESSAGE")
        
        print self.message_log
        #QTest.log()
        
        
        QTest.mousePress(iface.mapCanvas(), QtCore.Qt.LeftButton)
        #QTest.mouseMove(iface.mapCanvas())
        #QTest.mouseRelease(iface.mapCanvas(), QtCore.Qt.LeftButton)
        

        total_area = 0.0
        for feature in layer.getFeatures():
            total_area += feature.geometry().area()

        print layer.dataProvider().featureCount()
        print total_area

    def test_fonctionnel2(self):
        self.assertTrue(1 == 1, "")
if __name__ == '__main__':
    unittest.main()
