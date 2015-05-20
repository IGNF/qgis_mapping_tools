from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from common import Common

class Fusion(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.pathPointsList = []
        #self.canvas.mapToolSet.connect(self.changeMapTool)
    #def changeMapTool(self, newTool):
    #    print newTool

    def activate(self):
        print 'fusion activate'
        self.canvas.setCursor(self.cursor)
        self.canvas.setMouseTracking(False)
        self.activated.emit()
        if self.canvas.currentLayer():
            self.updateSpIdx(self.canvas.currentLayer())
        self.canvas.currentLayerChanged.connect(self.updateSpIdx)
        
    def deactivate(self):
        print 'fusion deactivate'
        self.canvas.setMouseTracking(True)
        self.deactivated.emit()
        try:
            self.canvas.currentLayer().featureAdded.disconnect( self.featureAddedEvent )
            self.canvas.currentLayer().featureDeleted.disconnect( self.featureDeletedEvent )
        except:
            pass
        self.canvas.currentLayerChanged.disconnect(self.updateSpIdx)

    def updateSpIdx(self, currentLayer):
        if currentLayer == None:
            return
        # Create a dictionary of all features
        #self.featuresDict = {f.id(): f for f in currentLayer.getFeatures()}
        # Build a spatial index
        self.index = QgsSpatialIndex(currentLayer.getFeatures())
        #for f in self.featuresDict.values():
        #    self.index.insertFeature(f)
        
        currentLayer.featureAdded.connect( self.featureAddedEvent )
        currentLayer.featureDeleted.connect( self.featureDeletedEvent )

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        layer.beginEditCommand("Features fusion")
        self.newFeat = None
        self.r = QgsRubberBand(self.canvas, False)
        self.r.setColor(QColor(255, 71, 25))
        self.r.setWidth(0.2)
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.pathPointsList.append(QgsPoint(point[0], point[1]))
        if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0:
            self.itemsReset()
            return

    def canvasMoveEvent(self, event):
        layer = self.canvas.currentLayer()
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        #selectedFeatureBbox = QgsGeometry.fromPoint(QgsPoint(point[0], point[1])).boundingBox()
        if self.newFeat == None:
            intersectFeatIds = self.index.nearestNeighbor(QgsPoint(point[0], point[1]),0)
            for fId in intersectFeatIds:
                #f = self.featuresDict[fId]
                req = QgsFeatureRequest(fId)
                for f in layer.getFeatures(req):
                    if f.geometry().intersects(QgsGeometry.fromPoint(QgsPoint(point[0], point[1]))):
                        self.newFeat = f
        self.pathPointsList.append(QgsPoint(point[0], point[1]))
        self.r.setToGeometry(QgsGeometry.fromPolyline(self.pathPointsList), None)

    def canvasReleaseEvent(self, event):
        # create a feature
        try:
            ft = QgsFeature()
            mousePathGeom = QgsGeometry.fromPolyline(self.pathPointsList)
            layer = self.canvas.currentLayer()
            
            if not mousePathGeom == None:
                ft.setGeometry(mousePathGeom)
                if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0 or self.newFeat == None:
                    self.itemsReset()
                    layer.destroyEditCommand()
                    return
                layer.removeSelection()
    
                featuresToFusionList = [self.newFeat.id()]
    
                selectedFeatureBbox = ft.geometry().boundingBox()
                intersectFeatIds = self.index.intersects(selectedFeatureBbox)
                for fId in intersectFeatIds:
                    #f = self.featuresDict[fId]
                    req = QgsFeatureRequest(fId)
                    for f in layer.getFeatures(req):
                        if f.geometry().intersects(ft.geometry()):
                            if fId not in featuresToFusionList:
                                self.newFeat.setGeometry(self.newFeat.geometry().combine(f.geometry()))
                                featuresToFusionList.append(f.id())
                layer.addFeature(self.newFeat)
                # Get newly added feature
                f = self.newFeat
                fid = f.id()
                self.index.insertFeature({fid: f}.values()[0])
                #self.featuresDict[fid] = f
                for fId in featuresToFusionList:
                    #f = self.featuresDict[fId]
                        #if successOnDel:
                        #    del self.featuresDict[fId]
                        layer.deleteFeature(fId)
    
                layer.setSelectedFeatures([])
                
            self.itemsReset()
            layer.endEditCommand()
            
        except:
            self.itemsReset()
            layer.destroyEditCommand()
            raise 

    def featureAddedEvent(self, feature):
        req = QgsFeatureRequest(feature)
        for f in self.canvas.currentLayer().getFeatures(req):
            self.index.insertFeature({feature: f}.values()[0])

    def featureDeletedEvent(self, feature):
        req = QgsFeatureRequest(feature)
        for f in self.canvas.currentLayer().getFeatures(req):
            self.index.deleteFeature(f)

    def itemsReset(self):
        self.pathPointsList = []
        self.canvas.scene().removeItem(self.r)