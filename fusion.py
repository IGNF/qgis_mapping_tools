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
        self.leftButton = False
        self.activated.connect(self.activateFusion)
        self.deactivated.connect(self.deactivateFusion)

    def activateFusion(self):
        self.canvas.setCursor(self.cursor)
        self.canvas.setMouseTracking(False)
        self.updateSpIdx(self.canvas.currentLayer())
        self.canvas.currentLayerChanged.connect(self.updateSpIdx)
        
    def deactivateFusion(self):
        self.canvas.setMouseTracking(True)
        try:
            self.canvas.currentLayerChanged.disconnect(self.updateSpIdx)
        except:
            pass
        
    
    def updateSpIdx(self, currentLayer):
        if currentLayer == None:
            return
        self.index = QgsSpatialIndex(currentLayer.getFeatures())

    def canvasPressEvent(self, event):
        if event.button() == 1:
            self.canvas.currentLayer().featureAdded.connect( self.featureAddedEvent )
            self.canvas.currentLayer().featureDeleted.connect( self.featureDeletedEvent )
            self.leftButton = True 
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
        if not self.leftButton:
            return
        layer = self.canvas.currentLayer()
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        #selectedFeatureBbox = QgsGeometry.fromPoint(QgsPoint(point[0], point[1])).boundingBox()
        if self.newFeat == None:
            intersectFeatIds = self.index.nearestNeighbor(QgsPoint(point[0], point[1]),0)
            for fId in intersectFeatIds:
                req = QgsFeatureRequest(fId)
                for f in layer.getFeatures(req):
                    if f.geometry().intersects(QgsGeometry.fromPoint(QgsPoint(point[0], point[1]))):
                        self.newFeat = f
        self.pathPointsList.append(QgsPoint(point[0], point[1]))
        self.r.setToGeometry(QgsGeometry.fromPolyline(self.pathPointsList), None)

    def canvasReleaseEvent(self, event):
        if not self.leftButton:
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

                selectedFeatureBbox = ft.geometry().boundingBox()
                intersectFeatIds = self.index.intersects(selectedFeatureBbox)
                for fId in intersectFeatIds:
                    req = QgsFeatureRequest(fId)
                    for f in layer.getFeatures(req):
                        if f.geometry().intersects(ft.geometry()):
                            if fId not in featuresToFusionList:
                                self.newFeat.setGeometry(self.newFeat.geometry().combine(f.geometry()))
                                featuresToFusionList.append(f.id())
                                
                if len(featuresToFusionList) == 1:
                    self.itemsReset()
                    layer.destroyEditCommand()
                    return
                layer.addFeature(self.newFeat)
                # Get newly added feature
                f = self.newFeat
                fid = f.id()
                self.index.insertFeature({fid: f}.values()[0])
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

    def featureAddedEvent(self, feature):
        if self.canvas.currentLayer():
            req = QgsFeatureRequest(feature)
            for f in self.canvas.currentLayer().getFeatures(req):
                self.index.insertFeature({feature: f}.values()[0])

    def featureDeletedEvent(self, feature):
        if self.canvas.currentLayer():
            req = QgsFeatureRequest(feature)
            for f in self.canvas.currentLayer().getFeatures(req):
                self.index.deleteFeature(f)

    def itemsReset(self):
        try:
            self.canvas.currentLayer().featureAdded.disconnect( self.featureAddedEvent )
            self.canvas.currentLayer().featureDeleted.disconnect( self.featureDeletedEvent )
        except:
            pass
        self.pathPointsList = []
        self.canvas.scene().removeItem(self.r)