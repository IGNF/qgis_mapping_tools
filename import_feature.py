from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
import processing
from common import Common
from ogr import Layer


class ImportFeature(QgsMapTool):
    def __init__(self, iface):
        super(QgsMapTool, self).__init__(iface.mapCanvas())
        self.iface = iface
        self.activated.connect(self.activateImportFeature)
        self.activated.connect(self.deactivateImportFeature)
        self.moveLocked=False

    def activateImportFeature(self):
        for layer in self.iface.mapCanvas().layers():
            if layer.isEditable():
                self.destinationLayer = layer
                break
        self.iface.mapCanvas().setCursor(Qt.CrossCursor)
        self.updateSpIdx(self.iface.mapCanvas().currentLayer())
        self.iface.mapCanvas().currentLayerChanged.connect(self.updateSpIdx)
        
    def deactivateImportFeature(self):
        try:
            self.iface.mapCanvas().currentLayerChanged.disconnect(self.updateSpIdx)
        except:
            pass
    
    def updateSpIdx(self, currentLayer):
        if currentLayer == None:
            return
        self.index = QgsSpatialIndex(currentLayer.getFeatures())
    
    def getFeatureByPoint(self, point, layer):
        if layer == self.iface.mapCanvas().currentLayer():
            intersectFeatIds = self.index.nearestNeighbor(point.asPoint(),0)
            for fId in intersectFeatIds:
                req = QgsFeatureRequest(fId)
                for f in layer.getFeatures(req):
                    if f.geometry().intersects(point):
                        return f
        else:
            for feat in layer.getFeatures():
                featGeom= feat.geometry()
                if featGeom.intersects(point):
                    return feat
        return None

    def getGeomToImportByPoint(self, point):
        sourceFeature = self.getFeatureByPoint(point, self.iface.mapCanvas().currentLayer())
        if sourceFeature == None:
            print 'pas de feature source'
            return None
        destFeature =  self.getFeatureByPoint(point, self.destinationLayer)
        if destFeature == None:
            print 'pas de feature dest'
            return None
        
        self.iface.mapCanvas().currentLayer().setSelectedFeatures([sourceFeature])
        
        
        sourceGeom = sourceFeature.geometry()
        destGeom = destFeature.geometry()
        
        intersection = QgsGeometry(destGeom.intersection(sourceGeom.asPolyline()))
        print 'SOURCE' + str(sourceGeom.exportToWkt())
        print 'DEST' + str(destGeom.exportToWkt())
        print 'INTERSECTION WKT : '+str(intersection.exportToWkt())
        if intersection == None:
            print 'intersection none'
        if intersection.isMultipart():
            '''print 'inters multipart'
            for part in intersection.asGeometryCollection():
                if point.within(part):
                    print 'part found ? '+str(part)
                    return QgsGeometry(part)
            '''       
        return intersection

    def canvasPressEvent(self, event):
        self.destinationLayer.beginEditCommand("Import feature")
        x = event.pos().x()
        y = event.pos().y()
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        sourceFeature = self.getFeatureByPoint(QgsGeometry().fromPoint(point), self.iface.mapCanvas().currentLayer())
        featDest = self.getFeatureByPoint(QgsGeometry().fromPoint(point), self.destinationLayer)
        fields = featDest.fields()
        #geomToImport = sceneItem.asGeometry()
        #geomToImport = self.getGeomToImportByPoint(QgsGeometry().fromPoint(point))
        geometry = QgsGeometry.fromPolygon(featDest.geometry().asPolygon())
        convertedLine = QgsGeometry.fromPolyline(sourceFeature.geometry().asPolyline())
        print sourceFeature.geometry().exportToWkt()
        successOnReshape = featDest.geometry().reshapeGeometry(convertedLine.asPolyline())
        print 'reshaped ? '+str(successOnReshape)
        if successOnReshape == 0:
            # Create a new feature to hold the other half of the split
            diff = QgsFeature(featDest)
            # Calculate the difference between the original geometry and the first half of the split
            diff.setGeometry( geometry.difference(featDest.geometry()))
            # Add the two halves of the split to the memory layer
            self.destinationLayer.addFeatures([featDest])
            self.destinationLayer.addFeatures([diff])
            
            
        '''print type(geomToImport)
        featToAdd = QgsFeature(fields)
        featToAdd.setGeometry(geomToImport)
        print geomToImport.exportToWkt()
        print 'feat geom empty ? '+str(geomToImport.isGeosEmpty())
        print 'feat geom valid ? '+str(geomToImport.isGeosValid())
        
        diffToAdd = QgsFeature(featDest)
        diff = featDest.geometry().difference(geomToImport)
        print 'diff geom valid ? '+str(geomToImport.isGeosValid())
        if diff.isMultipart():
            print 'diff multipart'
            for part in diff.asGeometryCollection ():
                diffToAdd.setGeometry(part)
                print 'add part'
                print self.destinationLayer.addFeature(diffToAdd)
        else:
            diffToAdd.setGeometry(diff)
            print 'add diff'
            print self.destinationLayer.addFeature(diffToAdd)
        featToDelete = featDest
        print 'add feat'
        print self.destinationLayer.addFeature(featToAdd)
        print 'delete feat'
        print self.destinationLayer.deleteFeature(featToDelete.id())'''
        self.destinationLayer.endEditCommand()
        self.iface.mapCanvas().refresh()
    #===========================================================================
    # def canvasMoveEvent(self, event):
    #     
    #     for sceneItem in self.iface.mapCanvas().scene().items():
    #         if isinstance(sceneItem, QgsRubberBand):
    #             self.iface.mapCanvas().scene().removeItem(sceneItem)
    #     if self.moveLocked:
    #         return
    #      
    #     self.moveLocked = True
    #      
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     for sceneItem in self.iface.mapCanvas().scene().items():
    #         if isinstance(sceneItem, QgsRubberBand):
    #             self.iface.mapCanvas().scene().removeItem(sceneItem)
    #             #print 'there is a rb'
    #             '''if sceneItem == self.iface.mapCanvas().scene().itemAt(x, y):
    #                 print 'we are already in this rb'
    #                 self.moveLocked = False
    #                 return
    #             else:
    #                 #print 'we have been exiting the rb'
    #                 self.iface.mapCanvas().scene().removeItem(sceneItem)'''
    #      
    #     point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
    #     feat = self.getGeomToImportByPoint(QgsGeometry().fromPoint(point))
    #     if feat == None:
    #         #print 'no intersection found'
    #         self.moveLocked = False
    #         return
    #     #print 'rb will be create'
    #     r = QgsRubberBand(self.iface.mapCanvas(), False) # True = a polygon
    #     r2 = QgsRubberBand(self.iface.mapCanvas(), False)
    #     
    #     #print QgsGeometry.fromPolygon(feat.asPolygon()).exportToWkt()
    #     #r.setToGeometry(QgsGeometry.fromPolygon(feat.asPolygon()), None)
    #     
    #     geom = [[QgsPoint(785077.40631783090066165,6528218.61511803232133389), QgsPoint(784866.84519791696220636,6528060.64310676883906126), QgsPoint(784858.38920185202732682,6528223.98820148501545191), QgsPoint(785077.40631783090066165,6528218.61511803232133389)]]
    #     geom2 = [[QgsPoint(784892,6528197), QgsPoint(784944,6528168), QgsPoint(784905,6528122), QgsPoint(784892,6528197)]]
    #     r.setToGeometry(QgsGeometry.fromPolygon(geom), None)
    #     r2.setToGeometry(QgsGeometry.fromPolygon(geom2), None)
    #     r.setColor(QColor(255, 71, 25, 160))
    #     r2.setColor(QColor(255, 255, 255))
    #     #r.setBorderColor(QColor(255, 71, 25))
    #     r.setWidth(3)
    #     r2.setWidth(3)
    #     
    #     
    #     #print 'rb created'
    #     #QgsApplication.processEvents()
    #     self.moveLocked = False
    #     
    #===========================================================================