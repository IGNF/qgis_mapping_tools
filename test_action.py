from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from common import Common

        
class TestAction(QgsMapTool):
    def __init__(self, canvas):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.activated.connect(self.activateFusion)

    def activateFusion(self):
        print 'activate test'
        Common().popup('test action')
        
    def deactivateFusion(self):
        pass
    