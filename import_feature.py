from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt

from common import Common
from ogr import Layer


class ImportFeature(QgsMapTool):
    def __init__(self, iface):
        super(QgsMapTool, self).__init__(iface.mapCanvas())
        self.iface = iface
        self.activated.connect(self.activateImportFeature)
        self.activated.connect(self.deactivateImportFeature)

    def activateImportFeature(self):
        for layer in self.iface.mapCanvas().layers():
            if layer.isEditable():
                self.destinationLayer = layer
                break
        self.iface.mapCanvas().setCursor(Qt.CrossCursor)
        self.updateSpIdx(self.iface.mapCanvas().currentLayer())
        self.iface.mapCanvas().currentLayerChanged.connect(self.updateSpIdx)
        
    def deactivateImportFeature(self):
        try:
            self.iface.mapCanvas().currentLayerChanged.disconnect(self.updateSpIdx)
        except:
            pass
    
    def updateSpIdx(self, currentLayer):
        if currentLayer == None:
            return
        self.index = QgsSpatialIndex(currentLayer.getFeatures())
    
    def getFeatureByPoint(self, point, layer):
        if layer == self.iface.mapCanvas().currentLayer():
            intersectFeatIds = self.index.nearestNeighbor(point.asPoint(),0)
            for fId in intersectFeatIds:
                req = QgsFeatureRequest(fId)
                for f in layer.getFeatures(req):
                    if f.geometry().intersects(point):
                        return f
        else:
            for feat in layer.getFeatures():
                featGeom= feat.geometry()
                if featGeom.intersects(point):
                    return feat
        return None

    def getGeomToImportByPoint(self, point):
        sourceFeature = self.getFeatureByPoint(point, self.iface.mapCanvas().currentLayer())
        if sourceFeature == None:
            return None
        destFeature =  self.getFeatureByPoint(point, self.destinationLayer)
        if destFeature == None:
            return None
        
        sourceGeom = sourceFeature.geometry()
        destGeom = destFeature.geometry()
        
        intersection = destGeom.intersection(sourceGeom)
        
        return intersection

    def canvasPressEvent(self, event):
        self.destinationLayer.beginEditCommand("Import feature")
        x = event.pos().x()
        y = event.pos().y()
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        featDest = self.getFeatureByPoint(QgsGeometry().fromPoint(point), self.destinationLayer)
        fields = featDest.fields()
        for sceneItem in self.iface.mapCanvas().scene().items():
            if isinstance(sceneItem, QgsRubberBand) and sceneItem == self.iface.mapCanvas().scene().itemAt(x, y):
                geomToImport = sceneItem.asGeometry()
                featToAdd = QgsFeature(fields)
                featToAdd.setGeometry(geomToImport)
                diffToAdd = QgsFeature(featDest)
                diffToAdd.setGeometry(featDest.geometry().difference(geomToImport))
                featToDelete = featDest
                
                self.destinationLayer.addFeature(featToAdd)
                self.destinationLayer.addFeature(diffToAdd)
                self.destinationLayer.deleteFeature(featToDelete.id())
        self.destinationLayer.endEditCommand()
        self.iface.mapCanvas().refresh()
        
    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        for sceneItem in self.iface.mapCanvas().scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                if sceneItem == self.iface.mapCanvas().scene().itemAt(x, y):
                    return
                else:
                    self.iface.mapCanvas().scene().removeItem(sceneItem)
        
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        feat = self.getGeomToImportByPoint(QgsGeometry().fromPoint(point))
        if feat == None:
            return
        r = QgsRubberBand(self.iface.mapCanvas(), True)  # True = a polygon
        r.setToGeometry(QgsGeometry.fromPolygon(feat.asPolygon()), None)
        r.setColor(QColor(255, 71, 25))
        r.setFillColor(QColor(255, 71, 25, 160))
        r.setWidth(3)
        
        
        
    # import feature into destination layer
    def addFeature(self, feature, destLayer, attrValues = None):
        #print attrValues
        print 'feature to add validity : '+str(feature.isValid())
        #self.destinationLayer.setSelectedFeatures([feature.id()])
        #print self.destinationLayer.capabilitiesString()
        successOnAdd = destLayer.addFeature(feature)
        print successOnAdd
        #print 'add feature'
        #print successOnAdd
        if successOnAdd == True:
            # Get newly added feature
            if not attrValues == None:
                
                feature.setAttributes(attrValues)
                destLayer.updateFeature(feature)
                
            #print 'fin : ' +str(fid)
        else:
            #print 'Adding feature failed'
            return False
