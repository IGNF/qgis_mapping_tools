from qgis.gui import QgsMapTool
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint
from PyQt4.QtGui import QCursor, QPixmap
from PyQt4.QtCore import Qt
from common import Common

class Fusion(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.cursor = QCursor(Qt.CrossCursor)
        self.pathPointsList = []
        #self.run()

    def activate(self):
        print 'activate'
        self.canvas.setCursor(self.cursor)
        self.canvas.setMouseTracking(False)
        self.activated.emit()
    
    def deactivate(self):
        print 'deactivate'
        self.canvas.setMouseTracking(True)
        self.deactivated.emit()
    
    def canvasMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.pathPointsList.append(QgsPoint(point[0], point[1]))

    def canvasReleaseEvent(self, event):
        ## create a feature
        ft = QgsFeature()
        mousePathGeom = QgsGeometry.fromPolyline(self.pathPointsList)
        ft.setGeometry(mousePathGeom)
        layer = self.canvas.currentLayer()
        if not layer:
            return
        if layer.type() != QgsMapLayer.VectorLayer:
            # Ignore this layer as it's not a vector
            return
        if layer.featureCount() == 0:
            # There are no features - skip
            return
        
        layer.removeSelection()
        
        featuresToFusionList = []
        for f in layer.getFeatures():
            if f.geometry().intersects(ft.geometry()):
                featuresToFusionList.append(f.id())
        print len(featuresToFusionList)
        layer.setSelectedFeatures(featuresToFusionList)
        self.pathPointsList = []
        
    def run(self):
        Common().popup('run fusion')