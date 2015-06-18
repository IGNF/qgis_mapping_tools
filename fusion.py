from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsMapLayerRegistry
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from common import Common

class Fusion(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.mergedFeature = None
        self.trackPoints = []
        self.activated.connect(self.activateFusion)
        self.deactivated.connect(self.deactivateFusion)

    def activateFusion(self):
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        self.canvas.setMouseTracking(False)
        
    def deactivateFusion(self):
        self.canvas.setMouseTracking(True)
    
    def createMoveTrack(self, color, width):
        moveTrack = QgsRubberBand(self.canvas, True)
        moveTrack.setColor(color)
        moveTrack.setWidth(width)
        return moveTrack
    
    def getMoveTrack(self):
        for sceneItem in self.canvas.scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                return sceneItem
        return None
    
    def updateMoveTrack(self, point):
        self.trackPoints.append(point)
        moveTrack = self.getMoveTrack()
        if moveTrack:
            moveTrack.setToGeometry(QgsGeometry.fromPolyline(self.trackPoints), None)
            return moveTrack
        return None

    def isLayerValid(self, layer):
        if layer and layer.type() == QgsMapLayer.VectorLayer and layer.featureCount() > 0:
            return True
        return False

    def isMoveTrackValid(self):
        if self.getMoveTrack() and self.getMoveTrack().asGeometry():
            return True
        return False

    def resetAction(self):
        self.mergedFeature = None
        self.trackPoints = []
        self.canvas.scene().removeItem(self.getMoveTrack())

    def cancelAction(self):
        self.resetAction()
        self.canvas.currentLayer().destroyEditCommand()

    def terminateAction(self):
        self.canvas.refresh()
        self.resetAction()
        self.canvas.currentLayer().endEditCommand()
    
    def screenCoordsToMapPoint(self, x, y):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        mapPoint = QgsPoint(point[0], point[1])
        return mapPoint
    
    def getIntersectedGeom(self, geometry, layer):
        intersectedFeatures = []
        for feature in layer.getFeatures():
            if feature.geometry().intersects(geometry):
                intersectedFeatures.append(feature)
        return intersectedFeatures
    
    def getFirstIntersectedGeom(self, geometry, layer):
        for feature in layer.getFeatures():
            if feature.geometry().intersects(geometry):
                return feature
        return None
    
    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        layer.beginEditCommand("Features fusion")
        
        if not self.isLayerValid(layer) or event.button() != 1:
            self.cancelAction()
            return
        
        self.createMoveTrack(QColor(255, 71, 25), 0.2)
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        self.mergedFeature = self.getFirstIntersectedGeom(QgsGeometry.fromPoint(mapPoint), layer)
        self.updateMoveTrack(mapPoint)
            
    def canvasMoveEvent(self, event):
        layer = self.canvas.currentLayer()
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        if not self.mergedFeature:
            self.mergedFeature = self.getFirstIntersectedGeom(QgsGeometry.fromPoint(mapPoint), layer)
        self.updateMoveTrack(mapPoint)

    def canvasReleaseEvent(self, event):
        layer = self.canvas.currentLayer()
        
        if self.mergedFeature == None or event.button() != 1:
            self.cancelAction()
            return
        if not (self.isLayerValid(layer) and self.isMoveTrackValid()):
            self.cancelAction()
            return

        featuresToMerge = [self.mergedFeature.id()]
        for feature in self.getIntersectedGeom(self.getMoveTrack().asGeometry(), layer):
            if feature.id() not in featuresToMerge:
                self.mergedFeature.setGeometry(self.mergedFeature.geometry().combine(feature.geometry()))
                featuresToMerge.append(feature.id())

        if len(featuresToMerge) < 2:
            self.cancelAction()
            return
        layer.addFeature(self.mergedFeature)
        for fId in featuresToMerge:
            layer.deleteFeature(fId)
            
        self.terminateAction()