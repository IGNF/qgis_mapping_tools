
from qgis.gui import QgsMapTool, QgsMapCanvas
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsMapLayerRegistry
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
from custom_maptool import CustomMapTool
class Fusion(CustomMapTool):
    """
    /***************************************************************************
     Fusion Class
            
            Do the stuff merging features.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """
        Constructor.
    
        :param iface: Interface of QGIS.
        :type iface: QgisInterface
        """
        
        # Declare inheritance to CustomMapTool
        CustomMapTool.__init__(self, iface.mapCanvas())
        
        self.canvas = iface.mapCanvas()
        
        # Init feature resulting of merge operation.
        self.mergedFeature = None
        
        # Init hovered points list.
        self.trackPoints = []

    def activateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool activating.'''
        
        super(Fusion, self).activateMapTool()
        self.canvas.setCursor(QCursor(Qt.CrossCursor))
        self.canvas.setMouseTracking(False)
        
    def deactivateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool deactivating.'''
        
        super(Fusion, self).deactivateMapTool()
        self.canvas.setMouseTracking(True)
        
    def updateTrackPoints(self, point):
        '''
        Add point to the hovered by mouse cursor points list and update move track.
        
        :param point: Point to add.
        :type point: QgsPoint
        '''
        
        self.trackPoints.append(point)
        if len(self.trackPoints) > 1:
            self.updateMoveTrack(QgsGeometry.fromPolyline(self.trackPoints))

    def isLayerValid(self, layer):
        '''Check if layer is not None, of vector type and not empty.
        
            :param layer: Layer to check.
            :type layer: QgsMapLayer
            
            :return: True if valid. 
            :rtype: bool
        '''
        
        if layer and layer.type() == QgsMapLayer.VectorLayer and layer.featureCount() > 0:
            return True
        return False

    def resetAction(self):
        '''Reset merge operation (move track list and merged feature).'''
        
        self.mergedFeature = None
        self.trackPoints = []
        self.destroyMovetrack()

    def cancelAction(self):
        '''Cancel merge operation in case of problem.'''
        
        self.resetAction()
        self.canvas.currentLayer().destroyEditCommand()

    def terminateAction(self):
        '''Terminate merge operation in case of success.'''
        
        self.canvas.refresh()
        self.resetAction()
        self.canvas.currentLayer().endEditCommand()
        
    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        
        layer = self.canvas.currentLayer()
        
        # Begin an editing buffer that will let user to undo / redo action. 
        layer.beginEditCommand("Features fusion")
        
        if not self.isLayerValid(layer) or event.button() != 1: # Do action only if layer is valid and left mouse button is used.
            self.cancelAction()
            return
        
        # Init move track object.
        self.createMoveTrack()
        
        # Convert clicked point in pixel coordinates to map coordinates point
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        # Get if found a feature under the clicked point : it will be the reference feature for construct result feature.
        self.mergedFeature = self.getFirstIntersectedFeature(QgsGeometry.fromPoint(mapPoint), layer)
        
        # Begin to draw move track with the first clicked point.
        self.updateTrackPoints(mapPoint)
            
    def canvasMoveEvent(self, event):
        '''Override slot fired when mouse is moved.'''
        
        layer = self.canvas.currentLayer()
        
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        if not self.mergedFeature: # If the previous hovered points was not into a feature. 
            self.mergedFeature = self.getFirstIntersectedFeature(QgsGeometry.fromPoint(mapPoint), layer)
        
        # Draw move track.
        self.updateTrackPoints(mapPoint)

    def canvasReleaseEvent(self, event):
        '''Override slot fired when mouse is released.'''
        
        layer = self.canvas.currentLayer()
        
        if self.mergedFeature == None or event.button() != 1: # Cancel action if no hovered features or if right click.
            self.cancelAction()
            return
        if not (self.isLayerValid(layer) and self.isMoveTrackValid()): # Check objects validity.
            self.cancelAction()
            return
        
        # Init list of features to merge.
        featuresToMerge = [self.mergedFeature.id()]
        
        # Intersected features with move track geometry and merge them successively.
        for feature in self.getIntersectedFeatures(self.getMoveTrack().asGeometry(), layer):
            if feature.id() not in featuresToMerge: # Avoid duplication
                self.mergedFeature.setGeometry(self.mergedFeature.geometry().combine(feature.geometry()))
                featuresToMerge.append(feature.id())
        
        if len(featuresToMerge) < 2: # No features to merge
            self.cancelAction()
            return
        
        # Add result merge feature.
        if not layer.addFeature(self.mergedFeature): # Cancel all merge operation if fail.
            self.cancelAction()
            return
        
        # Delete merged features.
        for fId in featuresToMerge:
            if not layer.deleteFeature(fId): # Cancel all merge operation if fail.
                self.cancelAction()
                return
        
        self.terminateAction()

