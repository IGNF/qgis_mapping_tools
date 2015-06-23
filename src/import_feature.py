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
        CustomMapTool.__init__(self, iface.mapCanvas())
        
        self.canvas = iface.mapCanvas()
        self.moveLocked=False
        self.plugin_dir = os.path.dirname(__file__)
        self.importFeatureSelector = loadUi( os.path.join( self.plugin_dir, "importFeatureSelector.ui" ) )

    def activateMapTool(self):
        super(ImportFeature, self).activateMapTool()
        self.canvas.setCursor(Qt.CrossCursor)
        
        # Show the dialog
        self.importFeatureSelector.show()
        self.updateSourceLayerSelector()
        QgsMapLayerRegistry.instance().layersRemoved.connect(self.updateSourceLayerSelector)
        QgsMapLayerRegistry.instance().legendLayersAdded.connect(self.updateSourceLayerSelector)
        self.canvas.currentLayerChanged.connect(self.updateSourceLayerSelector)
        
    def deactivateMapTool(self):
        super(ImportFeature, self).deactivateMapTool()
        self.importFeatureSelector.close()
        try:
            QgsMapLayerRegistry.instance().layersRemoved.disconnect(self.updateSourceLayerSelector)
            QgsMapLayerRegistry.instance().legendLayersAdded.disconnect(self.updateSourceLayerSelector)
            self.canvas.currentLayerChanged.disconnect(self.updateSourceLayerSelector)
        except:
            pass

    def updateSourceLayerSelector(self):
        sourceLayerList = self.importFeatureSelector.findChildren(QListWidget)[0]
        sourceLayerList.clear()
        # replace canvas by iface.legendInterface if we want add all vector layers including non visible ones
        layers = self.canvas.layers()
        
        layerAdded = False
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer != self.canvas.currentLayer():
                sourceLayerList.addItem(layer.name())
                layerAdded = True
        if not layerAdded:
            sourceLayerList.addItem("Ajouter au moins une couche")
        sourceLayerList.setCurrentRow(0)

    def getSourceLayer(self):
        selectedItem = self.importFeatureSelector.findChildren(QListWidget)[0].currentItem()
        if selectedItem:
            sourceLayerName = selectedItem.text()
            for layer in self.canvas.layers():
                if layer.name() == sourceLayerName:
                    return layer
        return None

    def getGeomToImportByPoint(self, point):
        if point:
            sourceLayer = self.getSourceLayer()
            sourceFeature = self.getFirstIntersectedFeature(point, sourceLayer)
            destFeature =  self.getFirstIntersectedFeature(point, self.canvas.currentLayer())
            
            if sourceLayer and sourceFeature and destFeature:
                sourceGeom = sourceFeature.geometry()
                destGeom = destFeature.geometry()
                intersection = QgsGeometry(destGeom.intersection(sourceGeom))
                return intersection
        return None

    def canvasPressEvent(self, event):
        destinationLayer = self.canvas.currentLayer()
        
        destinationLayer.beginEditCommand("Import feature")
        
        mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
        
        featureToPierce = self.getFirstIntersectedFeature(QgsGeometry().fromPoint(mapPoint), destinationLayer)
        ringToImport = self.getGeomToImportByPoint(QgsGeometry().fromPoint(mapPoint))
        
        if ringToImport and featureToPierce:
            fields = featureToPierce.fields()
            ringFeature = QgsFeature(fields)
            ringFeature.setGeometry(ringToImport)
            if not destinationLayer.addFeature(ringFeature):
                destinationLayer.destroyEditCommand()
    
            differenceFeature = QgsFeature(featureToPierce)
            difference = featureToPierce.geometry().difference(ringToImport)
            if difference.isMultipart():
                for part in difference.asGeometryCollection():
                    differenceFeature.setGeometry(part)
                    if not destinationLayer.addFeature(differenceFeature):
                        destinationLayer.destroyEditCommand()
            else:
                differenceFeature.setGeometry(difference)
                if not destinationLayer.addFeature(differenceFeature):
                    destinationLayer.destroyEditCommand()
                
            if not destinationLayer.deleteFeature(featureToPierce.id()):
                destinationLayer.destroyEditCommand()
            destinationLayer.endEditCommand()
            self.canvas.refresh()