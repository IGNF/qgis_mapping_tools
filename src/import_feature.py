from qgis.core import *
from qgis.gui import *
from PyQt4.uic import *
from PyQt4.QtGui import QCursor, QPixmap, QColor, QGraphicsScene, QListWidget
from PyQt4.QtCore import Qt
import processing
from custom_maptool import CustomMapTool
import os.path


class ImportFeature(CustomMapTool):
    def __init__(self, iface):
        '''Constructor.
            :param iface : Interface of QGIS.
            :type iface : QgisInterface
        '''
        
        # Declare inheritance to CustomMapTool class
        CustomMapTool.__init__(self, iface.mapCanvas())
        
        self.canvas = iface.mapCanvas()
        
        # Load Qt UI dialog widget from dir path
        pluginDirectory = os.path.dirname(__file__)
        self.importFeatureSelector = loadUi( os.path.join(pluginDirectory, "importFeatureSelector.ui"))

    def activateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool activating.'''
        
        # Declare override.
        super(ImportFeature, self).activateMapTool()
        
        # Change mouse cursor form.
        self.canvas.setCursor(Qt.CrossCursor)
        
        # Show the dialog
        self.importFeatureSelector.show()
        self.updateSourceLayerSelector()
        QgsMapLayerRegistry.instance().layersRemoved.connect(self.updateSourceLayerSelector)
        QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.updateSourceLayerSelector)
        self.canvas.currentLayerChanged.connect(self.updateSourceLayerSelector)
        
    def deactivateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool activating.'''
        
        # Declare override.
        super(ImportFeature, self).deactivateMapTool()
        
        self.importFeatureSelector.close()
        try:
            QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateSourceLayerSelector)
            QgsMapLayerRegistry.instance().legendLayersAdded.disconnect(self.updateSourceLayerSelector)
            self.canvas.currentLayerChanged.disconnect(self.updateSourceLayerSelector)
        except:
            pass

    def updateSourceLayerSelector(self):
        '''Update list dialog widget as soon as there is a change into layer tree.'''
        
        # Get layers list.
        sourceLayerList = self.importFeatureSelector.findChildren(QListWidget)[0]
        sourceLayerList.clear()
        
        layers = self.canvas.layers() # replace canvas by iface.legendInterface to include non visible layers on the map.
        
        # Fill the list.
        layerAdded = False
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer != self.canvas.currentLayer():
                sourceLayerList.addItem(layer.name())
                layerAdded = True
        if not layerAdded:
            sourceLayerList.addItem("Ajouter au moins une couche")
        sourceLayerList.setCurrentRow(0)

    def getSourceLayer(self):
        '''Get layer containing features to import from selected row into layers list widget.
            :returns: Vector layer or None if not found.
            :rtype: QgsVectorLayer or None
        '''
        
        selectedItem = self.importFeatureSelector.findChildren(QListWidget)[0].currentItem()
        if selectedItem:
            sourceLayerName = selectedItem.text()
            for layer in self.canvas.layers():
                if layer.name() == sourceLayerName:
                    return layer
        return None

    def getGeomToImportByPoint(self, point):
        '''Get intersection between features of destination layer and source layer under a point.
            :param: Geometry containing point.
            :type: QgsGeometry
            
            :returns: Intersection or None if not found.
            :rtype: QgsGeometry or None
        '''
        
        if point:
            sourceLayer = self.getSourceLayer()
            
            # Get features contained by source layer and destination layer and intersected by point.
            sourceFeature = self.getFirstIntersectedFeature(point, sourceLayer)
            destFeature =  self.getFirstIntersectedFeature(point, self.canvas.currentLayer())
            
            if sourceLayer and sourceFeature and destFeature:
                sourceGeom = sourceFeature.geometry()
                destGeom = destFeature.geometry()
                
                intersection = QgsGeometry(destGeom.intersection(sourceGeom))
                
                return intersection
        return None

    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''
        
        destinationLayer = self.canvas.currentLayer()
        
        # Begin buffer that will let user to undo / redo action. 
        destinationLayer.beginEditCommand("Import feature")
        
        # Convert pixel coordinates of click event to QgsPoint in map coordinates.
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        # Find feature in destination layer that will be pierced by the import of new feature.
        featureToPierce = self.getFirstIntersectedFeature(QgsGeometry().fromPoint(mapPoint), destinationLayer)
        # Find geometry of feature to import.
        ringToImport = self.getGeomToImportByPoint(QgsGeometry().fromPoint(mapPoint))
        
        if ringToImport and featureToPierce:
            
            # Contruct a new feature with fields of destination layer features and geometry corresponding to intersection.
            fields = featureToPierce.fields()
            ringFeature = QgsFeature(fields)
            ringFeature.setGeometry(ringToImport)
            
            # Add new feature to destination layer
            if not destinationLayer.addFeature(ringFeature):
                destinationLayer.destroyEditCommand() # If fail, undo all action and destroy editing buffer.
            
            # Construct a new feature retrieving pierced feature fields values.
            differenceFeature = QgsFeature(featureToPierce)
            difference = featureToPierce.geometry().difference(ringToImport)
            
            if difference.isMultipart(): # If multipart difference, we add as many features as parts.
                for part in difference.asGeometryCollection():
                    differenceFeature.setGeometry(part)
                    if not destinationLayer.addFeature(differenceFeature):
                        destinationLayer.destroyEditCommand()
            else:
                differenceFeature.setGeometry(difference)
                
                # Add difference feature or undo all action if fail.
                if not destinationLayer.addFeature(differenceFeature):
                    destinationLayer.destroyEditCommand()
            
            # Delete origin pierced feature or undo all action if fail.
            if not destinationLayer.deleteFeature(featureToPierce.id()):
                destinationLayer.destroyEditCommand()
                
            # End of editing buffer
            destinationLayer.endEditCommand()
            
            self.canvas.refresh()