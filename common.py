from PyQt4.QtGui import QMessageBox
from qgis.gui import QgsMapCanvas
from qgis.core import QgsGeometry, QgsPoint, QgsSpatialIndex, QgsFeatureRequest, QgsMapLayer
#from qgis.utils import iface

class Common:
    def __init__(self, iface):
        self.indexCatalog = dict()
        self.iface = iface
    def popup(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
    
    def screenCoordsToMapPoint(self, x, y):
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        mapPoint = QgsPoint(point[0], point[1])
        return mapPoint
    
    def getLayerBySpatialIndex(self, spatialIndex):
        for key, value in self.indexCatalog.iteritems():
            if value == spatialIndex:
                return key
        return None
        
    def getIntersectedFeatIdsWithSpatialIdx(self, geometry, spatialIndex):
        if geometry.type() == 0:
            intersectFeatIds = spatialIndex.nearestNeighbor(geometry.asPoint(),0)
        elif geometry.type() == 1 or geometry.type() == 2:
            intersectFeatIds = spatialIndex.intersects(geometry.boundingBox())
        if intersectFeatIds:
            return intersectFeatIds
        else:
            return None
      
    def getIntersectedFeatures(self, geometry, layer):
        intersectedFeatures = []
        if layer in self.indexCatalog:
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.indexCatalog[layer])
            for featureId in intersectFeatIds:
                req = QgsFeatureRequest(featureId)
                for feature in layer.getFeatures(req):
                    if feature.geometry().intersects(geometry):
                        intersectedFeatures.append(feature)
        else:
            for feature in layer.getFeatures():
                if feature.geometry().intersects(geometry):
                    intersectedFeatures.append(feature)
        return intersectedFeatures
    
    def getFirstIntersectedFeature(self, geometry, layer):
        if layer in self.indexCatalog:
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.indexCatalog[layer])
            if intersectFeatIds:
                for featureId in intersectFeatIds:
                    req = QgsFeatureRequest(featureId)
                    for feature in layer.getFeatures(req):
                        if feature.geometry().intersects(geometry):
                            return feature
        for feature in layer.getFeatures():
            if feature.geometry().intersects(geometry):
                return feature
        return None
    
    def setSpatialIndexToLayer(self, layer):
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            spatialIndex = QgsSpatialIndex(layer.getFeatures())
            self.indexCatalog[layer] = spatialIndex
            return spatialIndex
        return None
    
    def getSpatialIndexByLayer(self, layer):
        if layer in self.indexCatalog:
            return self.indexCatalog[layer]
        return None
    
    def removeSpatialIndexFromLayer(self, layer):
        if layer in self.indexCatalog:
            del self.indexCatalog[layer]
            return True
        return False
    
    def addFeatureToSpatialIndex(self, layer, featureToAdd):
        spatialIndex = self.indexCatalog[layer]
        spatialIndex.insertFeature({featureToAdd.id(): featureToAdd}.values()[0])
        return spatialIndex
    
    def deleteFeatureToSpatialIndex(self, layer, featureToDelete):
        spatialIndex = self.indexCatalog[layer]
        spatialIndex.deleteFeature(featureToDelete)
        return spatialIndex
    