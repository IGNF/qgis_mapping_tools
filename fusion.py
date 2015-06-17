from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsMapLayerRegistry
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from common import Common

class Fusion(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.pathPointsList = []
        self.blockAction = False
        self.activated.connect(self.activateFusion)
        self.deactivated.connect(self.deactivateFusion)
        #self.layerCatalog = {}

    def activateFusion(self):
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        self.canvas.setMouseTracking(False)
        '''self.setSpatialIndex(self.canvas.layers())
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.removeSpatialIndex)
        QgsMapLayerRegistry.instance().layersAdded.connect(self.setSpatialIndex)
        self.canvas.currentLayerChanged.connect(self.setSpatialIndex)'''
        
    def deactivateFusion(self):
        self.canvas.setMouseTracking(True)
        '''try:
            self.canvas.currentLayerChanged.disconnect(self.setSpatialIndex)
            QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.removeSpatialIndex)
            QgsMapLayerRegistry.instance().layersAdded.disconnect(self.setSpatialIndex)
        except:
            pass'''
        
    '''def removeSpatialIndex(self, layerId):
        print 'de ' +str(len(self.canvas.layers()))
        layer = self.getLayerById(layerId)
        if layer:
            print 'del an idx'
            del self.layerCatalog[layer]

    
    def setSpatialIndex(self, layers):
        for layer in layers:
            index = QgsSpatialIndex(layer.getFeatures())
            self.layerCatalog[layer] = index

    def getLayerById(self, layerId):
        print len(self.canvas.layers())
        print layerId
        for layer in self.canvas.layers():
            print layer.id()
            if layer.id() == layerId:
                return layer
        return None

    def getSpatialIdxFromLayer(self, layer):
        return self.layerCatalog[layer]
'''
    
    def getMoveTrace(self):
        for sceneItem in self.canvas.scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                return sceneItem
        return None
    
    def createMoveTrace(self, color, width):
        moveTrace = QgsRubberBand(self.canvas, False)
        moveTrace.setColor(color)
        moveTrace.setWidth(width)
        return moveTrace
    
    def updateMoveTrace(self, pointsList):
        moveTrace = self.getMoveTrace()
        if moveTrace:
            moveTrace.setToGeometry(QgsGeometry.fromPolyline(pointsList), None)
            return moveTrace
        return None
    
    def screenCoordsToMapPoint(self, x, y):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        mapPoint = QgsPoint(point[0], point[1])
        return mapPoint
    
    def canvasPressEvent(self, event):
        if event.button() != 1:
            self.itemsReset()
            return
        #print self.layerCatalog
        #self.canvas.currentLayer().featureAdded.connect(self.addFeatureToSpatialIndex)
        #self.canvas.currentLayer().featureDeleted.connect(self.deleteFeatureFromSpatialIndex)
        layer = self.canvas.currentLayer()
        layer.beginEditCommand("Features fusion")
        self.createMoveTrace(QColor(255, 71, 25), 0.2)
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        self.pathPointsList.append(mapPoint)
        if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0:
            self.itemsReset()
            return
            
    def canvasMoveEvent(self, event):
        layer = self.canvas.currentLayer()
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        '''intersectFeatIds = self.getSpatialIdxFromLayer(layer).nearestNeighbor(QgsPoint(point[0], point[1]),0)
        
        for fId in intersectFeatIds:
            req = QgsFeatureRequest(fId)
            for f in layer.getFeatures(req):'''
        i = 0
        for f in layer.getFeatures():
            if f.geometry().intersects(QgsGeometry.fromPoint(mapPoint)):
                if i == 0:
                    self.newFeat = f
                    i = 1
        self.pathPointsList.append(mapPoint)
        
        self.updateMoveTrace(self.pathPointsList)

    def canvasReleaseEvent(self, event):
        
        if event.button() != 1:
            self.itemsReset()
            return
        # create a feature
        try:
            ft = QgsFeature()
            layer = self.canvas.currentLayer()
            mousePathGeom = QgsGeometry.fromPolyline(self.pathPointsList)
            if not mousePathGeom == None:
                ft.setGeometry(mousePathGeom)
                if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0 or self.newFeat == None:
                    self.itemsReset()
                    layer.destroyEditCommand()
                    return
                layer.removeSelection()

                featuresToFusionList = [self.newFeat.id()]

                '''selectedFeatureBbox = ft.geometry().boundingBox()
                intersectFeatIds = self.getSpatialIdxFromLayer(layer).intersects(selectedFeatureBbox)
                for fId in intersectFeatIds:
                    f = self.getCurrentLayerFeatureById(fId)'''
                for f in layer.getFeatures():
                    if f.geometry().intersects(ft.geometry()):
                        if f.id() not in featuresToFusionList:
                            self.newFeat.setGeometry(self.newFeat.geometry().combine(f.geometry()))
                            featuresToFusionList.append(f.id())
                                
                if len(featuresToFusionList) == 1:
                    self.itemsReset()
                    layer.destroyEditCommand()
                    return
                layer.addFeature(self.newFeat)
                # Get newly added feature
                f = self.newFeat
                for fId in featuresToFusionList:
                    layer.deleteFeature(fId)
    
                layer.setSelectedFeatures([])
                self.itemsReset()
                layer.endEditCommand()
            else:
                self.itemsReset()
                layer.destroyEditCommand()
                return
            
        except:
            self.itemsReset()
            layer.destroyEditCommand()
            raise 

    '''def addFeatureToSpatialIndex(self, featureId):
        featureToAdd = self.getCurrentLayerFeatureById(featureId)
        if featureToAdd:
            self.getSpatialIdxFromLayer(self.canvas.currentLayer()).insertFeature({featureId: featureToAdd}.values()[0])

    def deleteFeatureFromSpatialIndex(self, featureId):
        featureToDelete = self.getCurrentLayerFeatureById(featureId)
        if featureToDelete:
            self.getSpatialIdxFromLayer(self.canvas.currentLayer()).deleteFeature(featureToDelete)
                
    def getCurrentLayerFeatureById(self, featureId):
        if self.canvas.currentLayer():
            req = QgsFeatureRequest(featureId)
            for feature in self.canvas.currentLayer().getFeatures(req):
                return feature
        return None
'''
    def itemsReset(self):
        '''self.canvas.currentLayer().featureAdded.disconnect( self.addFeatureToSpatialIndex )
        self.canvas.currentLayer().featureDeleted.disconnect( self.deleteFeatureFromSpatialIndex )'''
        self.pathPointsList = []
        self.canvas.scene().removeItem(self.getMoveTrace())