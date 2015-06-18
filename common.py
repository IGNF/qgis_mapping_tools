from PyQt4.QtGui import QMessageBox
from qgis.gui import QgsMapCanvas
from qgis.core import QgsGeometry, QgsPoint
from qgis.utils import iface

class Common:
    def __init__(self):
        pass
    
    def popup(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
    
    def screenCoordsToMapPoint(self, x, y):
        point = iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
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
    
