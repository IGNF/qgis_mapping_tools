
from PyQt4.QtGui import QMessageBox, QPixmap, QColor, QGraphicsScene
from qgis.gui import QgsMapCanvas, QgsMapTool, QgsRubberBand
from qgis.core import QgsGeometry, QgsPoint, QgsSpatialIndex, QgsFeatureRequest, QgsMapLayer, QgsMapLayerRegistry

class CustomMapTool(QgsMapTool):
    """
    /***************************************************************************
     CustomMapTool Class
            
            Class that inherits from QgsMapTools and contains common stuff to
            map tools developed for the plugin.  
     ***************************************************************************/
    """
    def __init__(self, canvas):
        """Constructor :
    
        :param canvas: The map canvas..
        :type canvas: QgsMapCanvas
        """
        # Declare inheritance to QgsMapTool class.
        super(QgsMapTool, self).__init__(canvas)

        # Attributes.
        self.canvas = canvas
        self.indexCatalog = dict()

        # Slots to activate / deactivate the tool
        self.activated.connect(self.activateMapTool)
        self.deactivated.connect(self.deactivateMapTool)

    def activateMapTool(self):
        '''Stuff to do when tool is activated.'''

        # Create a spatial index on the current layer when the tool is activated.
        if self.canvas.currentLayer() and self.canvas.currentLayer().type() == QgsMapLayer.VectorLayer:
            self.setSpatialIndexToLayer(self.canvas.currentLayer())
        self.canvas.currentLayerChanged.connect(self.setSpatialIndexToLayer)
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect(self.removeSpatialIndexFromLayerId)

    def deactivateMapTool(self):
        '''Stuff to do when tool is activated.'''
        self.indexCatalog = dict()
        # Disconnect signals if connected.
        try:
            self.canvas.currentLayerChanged.disconnect(self.setSpatialIndexToLayer)
            QgsMapLayerRegistry.instance().layerWillBeRemoved.disconnect(self.removeSpatialIndexFromLayerId)
        except:
            pass

    def popup(self, msg):
        '''Display a popup.
        
            :param msg: The message to display.
            :type msg: str
        '''
        
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()

    def screenCoordsToMapPoint(self, x, y):
        '''Converts pixel coordinates to a QgsPoint in map coordinates.
        
            :param x: x pixel coordinate.
            :type x: int
            
            :param y: y pixel coordinate.
            :type y: int
            
            :return: The corresponding point in map coordinates.
            :rtype: QgsPoint
        '''
        
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        mapPoint = QgsPoint(point[0], point[1])
        return mapPoint

    def getLayerBySpatialIndex(self, spatialIndex):
        '''Get layer corresponding to a given spatial index.
        
            :param spatialIndex: A spatial index.
            :type spatialIndex: QgsSpatialIndex
            
            :return: The layer corresponding to spatial index. None if not found.
            :rtype: QgsVectorLayer or None
        '''
        
        for key, value in self.indexCatalog.iteritems():
            if value == spatialIndex:
                return key
        return None

    def getIntersectedFeatIdsWithSpatialIdx(self, geometry, spatialIndex):
        '''Get the IDs of features that intersect a given geometry when the layer owning 
            features to intersect has a spatial index.
            
            :param geometry: Geometry we would features that intersect its.
            :type spatialIndex: QgsGeometry
            
            :param spatialIndex: Spatial index to use.
            :type spatialIndex: QgsSpatialIndex
            
            :return: IDs of features or None if no intersections found.
            :rtype: list or None
        '''
        
        intersectFeatIds=[]
        if geometry.type() == 0: # geometry is a point
            intersectFeatIds = spatialIndex.nearestNeighbor(geometry.asPoint(),0)
        elif geometry.type() == 1 or geometry.type() == 2: # geometry is a polyline or a polygon
            intersectFeatIds = spatialIndex.intersects(geometry.boundingBox())
        if intersectFeatIds:
            return intersectFeatIds
        else:
            return None

    def getIntersectedFeatures(self, geometry, layer):
        '''Get the features of a given layer that intersect a given geometry.
        
            :param geometry: Geometry we would features that intersect its.
            :type spatialIndex: QgsGeometry
            
            :param layer: Layer where find intersected features.
            :type layer: QgsVectorLayer
            
            :return: Features or None if no intersections found.
            :rtype: list or None
        '''
        
        intersectedFeatures = []
        if layer in self.indexCatalog:
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.getSpatialIndexByLayer(layer))
            for featureId in intersectFeatIds:
                req = QgsFeatureRequest(featureId)
                for feature in layer.getFeatures(req):
                    if feature.geometry().intersects(geometry):
                        intersectedFeatures.append(feature)
        else:
            for feature in layer.getFeatures():
                if feature.geometry().intersects(geometry):
                    intersectedFeatures.append(feature)
        return intersectedFeatures

    def getFirstIntersectedFeature(self, geometry, layer):
        '''Get the first feature found, of a given layer, that intersect a given geometry.
            useful to increase performances when one feature has to be found.
            
            :param geometry: Geometry we would features that intersect its.
            :type geometry: QgsGeometry
            
            :param layer: Layer where find intersected features.
            :type layer: QgsVectorLayer
            
            :return: Feature or None if no intersections found.
            :rtype: QgsFeature or None
        '''
        
        if layer in self.indexCatalog:
            intersectFeatIds = self.getIntersectedFeatIdsWithSpatialIdx(geometry, self.getSpatialIndexByLayer(layer))
            if intersectFeatIds:
                for featureId in intersectFeatIds:
                    req = QgsFeatureRequest(featureId)
                    for feature in layer.getFeatures(req):
                        if feature.geometry().intersects(geometry):
                            return feature
        for feature in layer.getFeatures():
            if feature.geometry().intersects(geometry):
                return feature
        return None

    def setSpatialIndexToLayer(self, layer):
        '''Create a spatial index to a given layer.
        
            :param layer: Vector layer.
            :type layer: QgsVectorLayer
            
            :return: Spatial index.
            :rtype: QgsSpatialIndex or None
        '''
        
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            
            # (Re)construct spatial index.
            if not layer in self.indexCatalog:
                spatialIndex = QgsSpatialIndex(layer.getFeatures())
                
                # Add spatial index to dictionary to retrieve it.
                self.indexCatalog[layer] = spatialIndex
                
                # Connect slots to layer changes to update spatial index.
                layer.featureAdded.connect(self.addFeatureToSpatialIndex)
                layer.featureDeleted.connect(self.deleteFeatureFromSpatialIndex)
                """"print 'debut catalog'
                for layer in self.indexCatalog:
                    print layer.name() + ' : ' +str(layer)
                print 'fin catalog'"""
                return spatialIndex
        return None
    
    def getSpatialIndexByLayer(self, layer):
        '''Get spatial index of a given layer.
        
            :param layer: Vector layer.
            :type layer: QgsVectorLayer
            
            :return: Spatial index.
            :rtype: QgsSpatialIndex or None
        '''
        
        if layer in self.indexCatalog:
            return self.indexCatalog[layer]
        return None
    
    def removeSpatialIndexFromLayerId(self, layerId):
        '''Remove spatial index from a given layer ID.
        
            :param layerId: Vector layer ID.
            :type layerId: int
        '''
        
        for layer in self.indexCatalog:
            if layer.id() == layerId:
                self.removeSpatialIndexFromLayer(layer)
                return

    def removeSpatialIndexFromLayer(self, layer):
        '''Remove spatial index from a given layer.
        
            :param layer: Vector layer.
            :type layer: QgsVectorLayer
        '''
        
        if layer in self.indexCatalog:
            del self.indexCatalog[layer]
            layer.featureAdded.disconnect(self.addFeatureToSpatialIndex)
            layer.featureDeleted.disconnect(self.deleteFeatureFromSpatialIndex)
            return True
        return False

    def getFeatureById(self, layer, featureId):
        '''Get the feature of a given layer by ID.
        
            :param layer: Layer where search feature.
            :type layer: QgsVectorLayer
            
            :param featureId: Feature ID.
            :type featureId: int
            
            :return: Feature or None if not found.
            :rtype: QgsFeature or None
        '''
        
        for feature in layer.getFeatures():
            if feature.id() == featureId:
                return feature
        return None
    
    def addFeatureToSpatialIndex(self, featureToAddId):
        '''Update spatial index when feature is added.
        
            :param featureToAddId: Feature ID.
            :type featureToAddId: int
            
            :return: Updated spatial index.
            :rtype: QgsSpatialIndex
        '''

        layer = self.canvas.currentLayer()
        if layer:
            spatialIndex = self.getSpatialIndexByLayer(layer)
            featureToAdd = self.getFeatureById(layer, featureToAddId)
            if featureToAdd and spatialIndex:
                spatialIndex.insertFeature({featureToAddId: featureToAdd}.values()[0])
    
    def deleteFeatureFromSpatialIndex(self, featureToDeleteId):
        '''Update spatial index when feature is deleted.
        
            :param featureToDeleteId: Feature ID.
            :type featureToDeleteId: int
            
            :return: Updated spatial index.
            :rtype: QgsSpatialIndex
        '''
        
        layer = self.canvas.currentLayer()
        if layer:
            spatialIndex = self.getSpatialIndexByLayer(layer)
            featureToDelete = self.getFeatureById(layer, featureToDeleteId)
            if featureToDelete and spatialIndex:
                spatialIndex.deleteFeature(featureToDelete)
    
    def createMoveTrack(self, line=True, color=QColor(255, 71, 25, 255), width=0.2):
        '''Create move track.
        
            :param line: Flag indicating if geometry to draw is a line (True)
                or a polygon(False).
            :type line: bool
        
            :param color: Color of line.
            :type color: QColor
            
            :param width: Width of line.
            :type width: int
            
            :return: Created rubber band. 
            :rtype: QgsRubberBand
        '''
        
        moveTrack = QgsRubberBand(self.canvas, line)
        moveTrack.setColor(color)
        moveTrack.setWidth(width)
        return moveTrack
    
    def getMoveTrack(self):
        '''Find and return move track.
        
            :return: Rubber band. 
            :rtype: QgsRubberBand
        '''
        
        for sceneItem in self.canvas.scene().items():
            if isinstance(sceneItem, QgsRubberBand):
                return sceneItem
        return None
    
    def updateMoveTrack(self, geometry):
        '''Update drawn move track.
        
            :param point: New point hovered by mouse cursor.
            :type point: QgsGeometry
        '''
        if self.getMoveTrack():
            if geometry.type() == 1 or geometry.type() == 2: # Geometry is polyline or polygon
                self.getMoveTrack().setToGeometry(geometry, None)
    
    def destroyMovetrack(self):
        '''Destroy drawn move track.'''
        if self.getMoveTrack():
            self.canvas.scene().removeItem(self.getMoveTrack())

    def isMoveTrackValid(self):
        '''Check if move track is not None and not empty.
            
            :return: True if valid. 
            :rtype: bool
        '''
        
        if self.getMoveTrack() and self.getMoveTrack().asGeometry():
            return True
        return False

    def isMoveTrackAtPos(self, x, y):
        '''Test existence of move track under the given position.
        
            :param x: Abciss position in pixels
            :type x: int
            
            :param y: Ordinate position in pixels
            :type y: int
        
            :return: True if move track, False else. 
            :rtype: bool
        '''
        pos = self.screenCoordsToMapPoint(x, y)
        if self.isMoveTrackValid():
            return self.getMoveTrack().asGeometry().contains(pos)
        return False
    