from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from common import Common

class Fusion(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.pathPointsList = []

    def activate(self):
        print 'activate'
        self.canvas.setCursor(self.cursor)
        self.canvas.setMouseTracking(False)
        self.activated.emit()
    
    def deactivate(self):
        print 'deactivate'
        self.canvas.setMouseTracking(True)
        self.deactivated.emit()

    def canvasPressEvent(self, event):
        self.r = QgsRubberBand(self.canvas, False)
        self.r.setColor(QColor(255, 71, 25))
        self.r.setWidth(0.2)
        layer = self.canvas.currentLayer()
        self.newFeat = QgsFeature
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.pathPointsList.append(QgsPoint(point[0], point[1]))
        if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0:
            self.itemsReset()
            return
        for f in layer.getFeatures():
            if f.geometry().intersects(QgsGeometry.fromPoint(QgsPoint(point[0], point[1]))):
                self.newFeat = f

    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.pathPointsList.append(QgsPoint(point[0], point[1]))
        self.r.setToGeometry(QgsGeometry.fromPolyline(self.pathPointsList), None)

    def canvasReleaseEvent(self, event):
        ## create a feature
        ft = QgsFeature()
        mousePathGeom = QgsGeometry.fromPolyline(self.pathPointsList)
        layer = self.canvas.currentLayer()
        
        if not mousePathGeom == None:
            ft.setGeometry(mousePathGeom)
            if not layer or layer.type() != QgsMapLayer.VectorLayer or layer.featureCount() == 0:
                self.itemsReset()
                return
            layer.removeSelection()
    
            featuresToFusionList = [self.newFeat]
            for f in layer.getFeatures():
                if f.geometry().intersects(ft.geometry()):
                    if f.id() not in featuresToFusionList:
                        self.newFeat.setGeometry(self.newFeat.geometry().combine(f.geometry()))
                        featuresToFusionList.append(f.id())
            #layer.setSelectedFeatures(featuresToFusionList)
            layer.dataProvider().addFeatures([self.newFeat])
            layer.dataProvider().deleteFeatures(featuresToFusionList)
            layer.setSelectedFeatures([])
        self.itemsReset()
    
    def itemsReset(self):
        self.pathPointsList = []
        self.canvas.scene().removeItem(self.r)