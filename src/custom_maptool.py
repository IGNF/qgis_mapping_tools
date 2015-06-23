from PyQt4.QtGui import QMessageBox
from qgis.gui import QgsMapCanvas, QgsMapTool
from qgis.core import QgsGeometry, QgsPoint, QgsSpatialIndex, QgsFeatureRequest, QgsMapLayer, QgsMapLayerRegistry

class CustomMapTool(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.indexCatalog = dict()
        self.indexCatalogCursor = None

        self.activated.connect(self.activateMapTool)
        self.deactivated.connect(self.deactivateMapTool)

    def activateMapTool(self):
        if self.canvas.currentLayer().type() == QgsMapLayer.VectorLayer:
            self.setSpatialIndexToLayer(self.canvas.currentLayer())
        self.canvas.currentLayerChanged.connect(self.setSpatialIndexToLayer)
        QgsMapLayerRegistry.instance().layerRemoved.connect(self.removeSpatialIndexFromLayerId)

    def deactivateMapTool(self):
        try:
            self.canvas.currentLayerChanged.disconnect(self.setSpatialIndexToLayer)
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self.removeSpatialIndexFromLayerId)
        except:
            pass

    def popup(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()

    def screenCoordsToMapPoint(self, x, y):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
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
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.getSpatialIndexByLayer(layer))
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
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.getSpatialIndexByLayer(layer))
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
        print self.indexCatalog
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            if layer in self.indexCatalog:
                self.removeSpatialIndexFromLayer(layer)
            spatialIndex = QgsSpatialIndex(layer.getFeatures())
            self.indexCatalog[layer] = spatialIndex
            self.indexCatalogCursor = layer
            layer.featureAdded.connect(self.addFeatureToSpatialIndex)
            layer.featureDeleted.connect(self.deleteFeatureFromSpatialIndex)
            return spatialIndex
        return None
    
    def getSpatialIndexByLayer(self, layer):
        if layer in self.indexCatalog:
            return self.indexCatalog[layer]
        return None
    
    def removeSpatialIndexFromLayerId(self, layerId):
        for layer, spatialIdx in self.indexCatalog:
            if layer.id() == layerId:
                self.removeSpatialIndexFromLayer(layer)
                return

    def removeSpatialIndexFromLayer(self, layer):
        if layer in self.indexCatalog:
            del self.indexCatalog[layer]
            layer.featureAdded.disconnect(self.addFeatureToSpatialIndex)
            layer.featureDeleted.disconnect(self.deleteFeatureFromSpatialIndex)
            return True
        return False

    def getFeatureById(self, layer, featureId):
        for feature in layer.getFeatures():
            if feature.id() == featureId:
                return feature
        return None
    
    def addFeatureToSpatialIndex(self, featureToAddId):
        layer = self.indexCatalogCursor
        spatialIndex = self.getSpatialIndexByLayer(layer)
        featureToAdd = self.getFeatureById(layer, featureToAddId)
        if featureToAdd:
            spatialIndex.insertFeature({featureToAddId: featureToAdd}.values()[0])
        return spatialIndex

    def deleteFeatureFromSpatialIndex(self, featureToDeleteId):
        layer = self.indexCatalogCursor
        spatialIndex = self.getSpatialIndexByLayer(layer)
        featureToDelete = self.getFeatureById(layer, featureToDeleteId)
        if featureToDelete:
            spatialIndex.deleteFeature(featureToDelete)
        return spatialIndex
