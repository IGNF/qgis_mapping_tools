from qgis.gui import QgsMapTool, QgsMapCanvas, QgsRubberBand
from qgis.core import QgsMapLayer, QgsMapToPixel, QgsFeature, QgsFeatureRequest, QgsGeometry, QgsPoint, QgsSpatialIndex, QgsMapLayerRegistry
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene
from PyQt4.QtCore import Qt
from custom_maptool import CustomMapTool

class Fusion(CustomMapTool):
    def __init__(self, iface):
        '''Constructor.
            :param iface : Interface of QGIS.
            :type iface : QgisInterface
        '''
        
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
    
    def createMoveTrack(self, color, width):
        '''Create move track.
            :param color : Color of line.
            :type color : QColor
            
            :param width : Width of line.
            :type width : int
            
            :returns: Created rubber band. 
            :rtype: QgsRubberBand
        '''
        
        moveTrack = QgsRubberBand(self.canvas, True)
        moveTrack.setColor(color)
        moveTrack.setWidth(width)
        return moveTrack
    
    def getMoveTrack(self):
        '''Find and returns move track.
            :returns: Rubber band. 
            :rtype: QgsRubberBand
        '''
        
        for sceneItem in self.canvas.scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                return sceneItem
        return None
    
    def updateMoveTrack(self, point):
        '''Update drawn move track.
            :param point : New point hovered by mouse cursor.
            :type point : QgsPoint
            
            :returns: Updated rubber band. 
            :rtype: QgsRubberBand
        '''
        
        self.trackPoints.append(point)
        moveTrack = self.getMoveTrack()
        if moveTrack:
            moveTrack.setToGeometry(QgsGeometry.fromPolyline(self.trackPoints), None)
            return moveTrack
        return None

    def isLayerValid(self, layer):
        '''Check if layer is not None, of vector type and not empty.
            :param layer : Layer to check.
            :type layer : QgsMapLayer
            
            :returns: True if valid. 
            :rtype: bool
        '''
        
        if layer and layer.type() == QgsMapLayer.VectorLayer and layer.featureCount() > 0:
            return True
        return False

    def isMoveTrackValid(self):
        '''Check if move track is not None and not empty.
            
            :returns: True if valid. 
            :rtype: bool
        '''
        
        if self.getMoveTrack() and self.getMoveTrack().asGeometry():
            return True
        return False

    def resetAction(self):
        '''Reset merge operation (move track list and merged feature).'''
        
        self.mergedFeature = None
        self.trackPoints = []
        self.canvas.scene().removeItem(self.getMoveTrack())

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
        self.createMoveTrack(QColor(255, 71, 25), 0.2)
        
        # Convert clicked point in pixel coordinates to map coordinates point
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        # Get if found a feature under the clicked point : it will be the reference feature for construct result feature.
        self.mergedFeature = self.getFirstIntersectedFeature(QgsGeometry.fromPoint(mapPoint), layer)
        
        # Begin to draw move track with the first clicked point.
        self.updateMoveTrack(mapPoint)
            
    def canvasMoveEvent(self, event):
        '''Override slot fired when mouse is moved.'''
        
        layer = self.canvas.currentLayer()
        
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        if not self.mergedFeature: # If the previous hovered points was not into a feature. 
            self.mergedFeature = self.getFirstIntersectedFeature(QgsGeometry.fromPoint(mapPoint), layer)
        
        # Draw move track.
        self.updateMoveTrack(mapPoint)

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