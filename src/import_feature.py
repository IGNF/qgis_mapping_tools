from __future__ import absolute_import
from qgis.core import *
from qgis.gui import *
from PyQt5.uic import *
from PyQt5.QtGui import QCursor, QPixmap, QColor
from PyQt5.QtWidgets import QGraphicsScene, QListWidget
from PyQt5.QtCore import Qt, pyqtSignal
from .custom_maptool import CustomMapTool
import os.path

class ImportFeature(CustomMapTool):
    """
    /***************************************************************************
     ImportFeature Class

            Do the stuff importing a feature from a vector layer to another.
     ***************************************************************************/
     """
    def __init__(self, iface):
        """
        Constructor :

        :param iface: Interface of QGIS.
        :type iface: QgisInterface
        """

        # Declare inheritance to CustomMapTool class
        CustomMapTool.__init__(self, iface.mapCanvas())

        self.iface = iface
        self.canvas = iface.mapCanvas()
        # Load Qt UI dialog widget from dir path
        pluginDirectory = os.path.dirname(__file__)
        self.sourceLayerSelector = loadUi( os.path.join(pluginDirectory, "sourcelayerselector.ui"))

    def activateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool activating.'''

        # Declare override.
        super(ImportFeature, self).activateMapTool()

        # Change mouse cursor form.
        self.canvas.setCursor(Qt.CrossCursor)

        # Show the dialog
        self.iface.addDockWidget( Qt.LeftDockWidgetArea, self.sourceLayerSelector)

        self.updateSourceLayerSelector()
        QgsProject.instance().layersRemoved.connect(self.updateSourceLayerSelector)
        QgsProject.instance().layersAdded.connect(self.updateSourceLayerSelector)
        self.canvas.currentLayerChanged.connect(self.updateSourceLayerSelector)
        if self.iface.layerTreeView().currentNode().parent():
            self.iface.layerTreeView().currentNode().parent().visibilityChanged.connect(self.updateSourceLayerSelector)
        self.setSourceLayerSpatialIdx()
        self.sourceLayerSelector.findChildren(QListWidget)[0].currentItemChanged.connect(self.setSourceLayerSpatialIdx)

    def deactivateMapTool(self):
        '''Override CustomMapTool method to add specific stuff at tool deactivating.'''

        # It is possible to test if signals are connected with receivers. Metaobject to get signatures of signals.
        '''metaobject = self.iface.layerTreeView().currentNode().metaObject()
        for i in range(metaobject.methodCount()):
            print(metaobject.method(i).signature())
        print 'cur lay ch sig : ' + str(self.canvas.receivers(SIGNAL("currentLayerChanged(QgsMapLayer*)")))
        print 'vis ch : ' + str(self.iface.layerTreeView().currentNode().receivers(SIGNAL("visibilityChanged(QgsLayerTreeNode*,Qt::CheckState)")))'''

        # Declare override.
        super(ImportFeature, self).deactivateMapTool()

        self.sourceLayerSelector.close()
        self.destroyMovetrack()

        try:
            QgsProject.instance().layersRemoved.disconnect(self.updateSourceLayerSelector)
        except:
            pass

        try:
            QgsProject.instance().layersAdded.disconnect(self.updateSourceLayerSelector)
        except:
            pass

        try:
            self.canvas.currentLayerChanged.disconnect(self.updateSourceLayerSelector)
        except:
            pass

        try:
            if self.iface.layerTreeView().currentNode().parent():
                self.iface.layerTreeView().currentNode().parent().visibilityChanged.disconnect(self.updateSourceLayerSelector)
        except:
            pass

    def setSourceLayerSpatialIdx(self):
        '''Index the source layer.'''

        if self.getSourceLayer() and self.getSourceLayer().featureCount() > 0:
            self.setSpatialIndexToLayer(self.getSourceLayer())

    def updateSourceLayerSelector(self):
        '''Update list dialog widget as soon as there is a change into layer tree.'''

        # Get layers list.
        sourceLayerList = self.sourceLayerSelector.findChildren(QListWidget)[0]
        sourceLayerList.clear()
        layers = self.canvas.layers() # replace canvas by iface.legendInterface() to include non visible layers on the map.

        # Fill the list.
        layerAdded = False
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer != self.canvas.currentLayer():
                sourceLayerList.addItem(layer.name())
                #layer.layerModified.connect(self.updateSourceLayerSelector)
                layerAdded = True
        if not layerAdded:
            sourceLayerList.addItem("Afficher au moins une autre couche vecteur")
        sourceLayerList.setCurrentRow(0)

    def getSourceLayer(self):
        '''Get layer containing features to import from selected row into layers list widget.

            :return: Vector layer or None if not found.
            :rtype: QgsVectorLayer or None
        '''

        selectedItem = self.sourceLayerSelector.findChildren(QListWidget)[0].currentItem()
        if selectedItem:
            sourceLayerName = selectedItem.text()
            return self.getLayerByName(sourceLayerName)
        return None

    def getLayerByName(self, layerName):
        '''Get layer by name.

            :param layerName: Layer name we want to retrieve.
            :type layerName: str

            :return: Vector layer or None if not found.
            :rtype: QgsVectorLayer or None
        '''
        for layer in self.canvas.layers():
            if layer.name() == layerName:
                return layer
        return None

    def getGeomToImportByPoint(self, point):
        '''Get intersection between features of destination layer and source layer under a point.

            :param point: Geometry containing point.
            :type point: QgsGeometry

            :return: Intersection or None if not found.
            :rtype: QgsGeometry or None
        '''

        if self.getSourceLayer():

            # Get features contained by source layer and destination layer and intersected by point.
            sourceFeature = self.getFirstIntersectedFeature(point, self.getSourceLayer())
            destFeature =  self.getFirstIntersectedFeature(point, self.canvas.currentLayer())

            if sourceFeature and destFeature:
                sourceGeom = sourceFeature.geometry()
                destGeom = destFeature.geometry()

                intersection = QgsGeometry(destGeom.intersection(sourceGeom))

                return intersection
        return None

    def canvasPressEvent(self, event):
        '''Override slot fired when mouse is pressed.'''

        if event.button() == 1: # Do action only if left button was clicked
            destinationLayer = self.canvas.currentLayer()

            # Convert pixel coordinates of click event to QgsPoint in map coordinates.
            mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())

            if destinationLayer and mapPoint:

                # Find feature in destination layer that will be pierced by the import of new feature.
                featureToPierce = self.getFirstIntersectedFeature(QgsGeometry().fromPointXY(QgsPointXY(mapPoint)), destinationLayer)
                # Find geometry of feature to import.
                ringToImport = self.getGeomToImportByPoint(QgsGeometry().fromPointXY(QgsPointXY(mapPoint)))

                if ringToImport and featureToPierce:

                    if not ringToImport.equals(featureToPierce.geometry()): # Do not import feature already into destination layer

                        # Begin buffer that will let user to undo / redo action.
                        destinationLayer.beginEditCommand("Import feature")

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
                        if not difference:
                            destinationLayer.destroyEditCommand()
                            self.popup('Geometrie invalide')
                            return

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
                        self.destroyMovetrack()

                        self.canvas.refresh()


    def canvasMoveEvent(self, event):
        '''Override slot fired when mouse is moved.'''

        #if not self.isMoveTrackAtPos(event.pos().x(), event.pos().y()): # If move track already computed, anything to do
        if self.getSourceLayer():
            mapPoint = self.screenCoordsToMapPoint(event.pos().x(), event.pos().y())
            ringToDisplay = self.getGeomToImportByPoint(QgsGeometry().fromPointXY(QgsPointXY(mapPoint)))
            if ringToDisplay:
                if not self.getMoveTrack():
                    self.createMoveTrack(False, QColor(255, 71, 25, 170))
                self.updateMoveTrack(ringToDisplay)
            else:
                self.destroyMovetrack()
