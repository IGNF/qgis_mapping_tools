from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt

from common import Common
from ogr import Layer


class ImportFeature(QgsMapTool):
    def __init__(self, iface, sourceLayer, destinationLayer):
        super(QgsMapTool, self).__init__(iface.mapCanvas())
        self.iface = iface
        self.sourceLayer = sourceLayer
        self.destinationLayer = destinationLayer

    def getFeatureByPoint(self, point):
        if self.iface.mapCanvas().currentLayer():
            cLayer = self.iface.mapCanvas().currentLayer()
            for feat in cLayer.getFeatures():
                featGeom= feat.geometry()
                if featGeom.intersects(point):
                    return feat
        return None

    def importFeature(self, sourceFeat):
        selectedGeom = sourceFeat.geometry()
        intersectedFeats = []
        for layer in self.iface.mapCanvas().layers():
            if layer.isEditable():
                destLayer = layer
                break

        if destLayer:
            for f in destLayer.getFeatures():
                if f.geometry().intersects(selectedGeom):
                    intersectedFeats.append(f)
        
        print intersectedFeats
    
        for intersectFeat in intersectedFeats:
             # Look up the feature from the dictionary and get the geometry
            intersectGeom = intersectFeat.geometry()
            # The destination layer feature geometry that entirely contains selected feature
            # is the geometry to hole
            
            intersection = intersectGeom.intersection(selectedGeom)
            intersectionArea = intersection.area()
            selectedArea = selectedGeom.area()
            if selectedArea > 0 and intersectionArea/selectedArea > 0.5 and selectedArea <= intersectGeom.area():
            #if selectedGeom.within(intersectGeom):
            
                # Intersect the polygon with the line. If they intersect, the feature will contain one half of the split
                #intersection = intersectGeom.intersection(selectedGeom)
                intersectFeatValues = intersectFeat.attributes()# if len(intersectFeat.attributes()) > 2 else None
                fields = intersectFeat.fields()
                # Calculate the difference between the original geometry and the first half of the split
                diff = QgsFeature(intersectFeat)
                diff.setGeometry(intersectGeom.difference(intersection))
                 # Multipart management
                if diff.geometry().isMultipart():
                    #print 'diff multipart'
                    tempFeature = QgsFeature(intersectFeat)
                    #i = 0
                    # Create a new feature using the geometry of each part
                    for part in diff.geometry().asGeometryCollection ():
                        
                        partArea = part.area()
                        if partArea < 20:
                            intersection = intersection.combine(part)
                        else:
                            tempFeature.setGeometry(part)
                            featureImported = self.addFeature(tempFeature, destLayer, intersectFeatValues)
                            print 'add diff (multipart case) : ' + str(featureImported)
                            if featureImported == False:
                                self.finished.emit(True)
                else:
                    #print 'diff no multipart'
                    featureImported = self.addFeature(diff, destLayer, intersectFeatValues)
                    print 'add diff (NOT multipart case): ' + str(featureImported)
                    if featureImported == False:
                        self.finished.emit(True)
                        return
                # Create a new feature to hold the other half of the split
                intersectionFeat = QgsFeature(fields)
                intersectionFeat.setGeometry(intersection)
                print intersectionFeat
                featureImported = self.addFeature(intersectionFeat, destLayer)
                print 'add feat : ' + str(featureImported)
                if featureImported == False:
                    #self.finished.emit(True)
                    return
                # Remove original feature from layer provider (shpfile), index and features dictionary
                successOnDelete = destLayer.deleteFeature(intersectFeat.id())
                print 'delete feat dest : ' + str(successOnDelete)
                break
        
    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        point = self.iface.mapCanvas().getCoordinateTransform().toMapCoordinates(x, y)
        feat = self.getFeatureByPoint(QgsGeometry().fromPoint(point))
        print feat
        if feat == None:
            return
        
        self.importFeature(feat)
    # import feature into destination layer
    def addFeature(self, feature, destLayer, attrValues = None):
        #print attrValues
        print 'feature to add validity : '+str(feature.isValid())
        #self.destinationLayer.setSelectedFeatures([feature.id()])
        #print self.destinationLayer.capabilitiesString()
        successOnAdd = destLayer.addFeature(feature)
        print successOnAdd
        #print 'add feature'
        #print successOnAdd
        if successOnAdd == True:
            # Get newly added feature
            if not attrValues == None:
                
                feature.setAttributes(attrValues)
                destLayer.updateFeature(feature)
                
            #print 'fin : ' +str(fid)
        else:
            #print 'Adding feature failed'
            return False
