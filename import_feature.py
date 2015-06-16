from qgis.core import *
from qgis.gui import *
from PyQt4.uic import *
from qgis.utils import iface
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene, QListWidget
from PyQt4.QtCore import Qt
import processing
from common import Common
import os.path


class ImportFeature(QgsMapTool):
    def __init__(self, iface):
        super(QgsMapTool, self).__init__(iface.mapCanvas())
        self.iface = iface
        self.activated.connect(self.activateImportFeature)
        self.deactivated.connect(self.deactivateImportFeature)
        self.moveLocked=False
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.importFeatureSelector = loadUi( os.path.join( self.plugin_dir, "importFeatureSelector.ui" ) )

    def activateImportFeature(self):
        for layer in self.iface.mapCanvas().layers():
            if layer == self.iface.mapCanvas().currentLayer():
                self.destinationLayer = layer
                break
        self.iface.mapCanvas().setCursor(Qt.CrossCursor)
        self.updateSpIdx(self.iface.mapCanvas().currentLayer())
        self.iface.mapCanvas().currentLayerChanged.connect(self.updateSpIdx)
        # show the dialog
        
        self.importFeatureSelector.show()
        QgsMapLayerRegistry.instance().layersRemoved.connect(self.updateSourceLayerSelector)
        QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.updateSourceLayerSelector)
        self.iface.mapCanvas().currentLayerChanged.connect(self.updateSourceLayerSelector)
        self.updateSourceLayerSelector()
        
    def deactivateImportFeature(self):
        QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateSourceLayerSelector)
        QgsMapLayerRegistry.instance().legendLayersAdded.disconnect(self.updateSourceLayerSelector)
        self.iface.mapCanvas().currentLayerChanged.disconnect(self.updateSourceLayerSelector)
        self.iface.mapCanvas().currentLayerChanged.disconnect(self.updateSpIdx)
        self.importFeatureSelector.close()

                
    def updateSourceLayerSelector(self):
        self.importFeatureSelector.findChildren(QListWidget)[0].clear()
        layers = self.iface.legendInterface().layers()

        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer and layer != self.iface.mapCanvas().currentLayer():
                self.importFeatureSelector.findChildren(QListWidget)[0].addItem(layer.name())
        self.importFeatureSelector.findChildren(QListWidget)[0].setCurrentRow(0)
    
    def updateSpIdx(self, currentLayer):
        if currentLayer == None:
            return
        self.index = QgsSpatialIndex(currentLayer.getFeatures())
    
    def getFeatureByPoint(self, point, layer):
        for feat in layer.getFeatures():
            featGeom= feat.geometry()
            if featGeom.intersects(point):
                return feat
        return None

    def getGeomToImportByPoint(self, point):
        sourceLayerName = self.importFeatureSelector.findChildren(QListWidget)[0].currentItem().text()
        sourceLayer = None
        for lyr in self.iface.mapCanvas().layers():
            if lyr.name()==sourceLayerName:
                sourceLayer = lyr
                break
        if not sourceLayer:
            return None
        
        sourceFeature = self.getFeatureByPoint(point, sourceLayer)
        if sourceFeature == None:
            return None
        destFeature =  self.getFeatureByPoint(point, self.destinationLayer)
        if destFeature == None:
            return None
        
        self.iface.mapCanvas().currentLayer().setSelectedFeatures([sourceFeature])
        
        
        sourceGeom = sourceFeature.geometry()
        destGeom = destFeature.geometry()
        
        intersection = QgsGeometry(destGeom.intersection(sourceGeom))
        if intersection.isMultipart():
            '''print 'inters multipart'
            for part in intersection.asGeometryCollection():
                if point.within(part):
                    print 'part found ? '+str(part)
                    return QgsGeometry(part)
            '''       
        return intersection

    def canvasPressEvent(self, event):
        self.destinationLayer.beginEditCommand("Import feature")
        x = event.pos().x()
        y = event.pos().y()
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        featDest = self.getFeatureByPoint(QgsGeometry().fromPoint(point), self.destinationLayer)
        if featDest == None:
            return
        fields = featDest.fields()
        #geomToImport = sceneItem.asGeometry()
        geomToImport = self.getGeomToImportByPoint(QgsGeometry().fromPoint(point))
        if not geomToImport:
            return
        featToAdd = QgsFeature(fields)
        featToAdd.setGeometry(geomToImport)
        
        diffToAdd = QgsFeature(featDest)
        diff = featDest.geometry().difference(geomToImport)
        if diff.isMultipart():
            for part in diff.asGeometryCollection ():
                diffToAdd.setGeometry(part)
                self.destinationLayer.addFeature(diffToAdd)
        else:
            diffToAdd.setGeometry(diff)
            self.destinationLayer.addFeature(diffToAdd)
        featToDelete = featDest
        self.destinationLayer.addFeature(featToAdd)
        self.destinationLayer.deleteFeature(featToDelete.id())
        self.destinationLayer.endEditCommand()
        self.iface.mapCanvas().refresh()
    #===========================================================================
    # def canvasMoveEvent(self, event):
    #     
    #     for sceneItem in self.iface.mapCanvas().scene().items():
    #         if isinstance(sceneItem, QgsRubberBand):
    #             self.iface.mapCanvas().scene().removeItem(sceneItem)
    #     if self.moveLocked:
    #         return
    #      
    #     self.moveLocked = True
    #      
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     for sceneItem in self.iface.mapCanvas().scene().items():
    #         if isinstance(sceneItem, QgsRubberBand):
    #             self.iface.mapCanvas().scene().removeItem(sceneItem)
    #             #print 'there is a rb'
    #             '''if sceneItem == self.iface.mapCanvas().scene().itemAt(x, y):
    #                 print 'we are already in this rb'
    #                 self.moveLocked = False
    #                 return
    #             else:
    #                 #print 'we have been exiting the rb'
    #                 self.iface.mapCanvas().scene().removeItem(sceneItem)'''
    #      
    #     point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
    #     feat = self.getGeomToImportByPoint(QgsGeometry().fromPoint(point))
    #     if feat == None:
    #         #print 'no intersection found'
    #         self.moveLocked = False
    #         return
    #     #print 'rb will be create'
    #     r = QgsRubberBand(self.iface.mapCanvas(), False) # True = a polygon
    #     r2 = QgsRubberBand(self.iface.mapCanvas(), False)
    #     
    #     #print QgsGeometry.fromPolygon(feat.asPolygon()).exportToWkt()
    #     #r.setToGeometry(QgsGeometry.fromPolygon(feat.asPolygon()), None)
    #     
    #     geom = [[QgsPoint(785077.40631783090066165,6528218.61511803232133389), QgsPoint(784866.84519791696220636,6528060.64310676883906126), QgsPoint(784858.38920185202732682,6528223.98820148501545191), QgsPoint(785077.40631783090066165,6528218.61511803232133389)]]
    #     geom2 = [[QgsPoint(784892,6528197), QgsPoint(784944,6528168), QgsPoint(784905,6528122), QgsPoint(784892,6528197)]]
    #     r.setToGeometry(QgsGeometry.fromPolygon(geom), None)
    #     r2.setToGeometry(QgsGeometry.fromPolygon(geom2), None)
    #     r.setColor(QColor(255, 71, 25, 160))
    #     r2.setColor(QColor(255, 255, 255))
    #     #r.setBorderColor(QColor(255, 71, 25))
    #     r.setWidth(3)
    #     r2.setWidth(3)
    #     
    #     
    #     #print 'rb created'
    #     #QgsApplication.processEvents()
    #     self.moveLocked = False
    #     
    #===========================================================================