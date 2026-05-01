# coding=utf-8
"""QGIS plugin implementation.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. note:: This source code was copied from the 'postgis viewer' application
     with original authors:
     Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk
     Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org
     Copyright (c) 2014 Tim Sutton, tim@linfiniti.com

"""

__author__ = "tim@linfiniti.com"
__revision__ = "$Format:%H$"
__date__ = "10/01/2011"
__copyright__ = (
    "Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and "
    "Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org"
    "Copyright (c) 2014 Tim Sutton, tim@linfiniti.com"
)

import logging

from qgis.core import QgsMapLayer, QgsProject
from qgis.PyQt.QtCore import QObject, pyqtSignal

LOGGER = logging.getLogger("QGIS")


class QgisInterface(QObject):
    """Class to expose QGIS objects and functions to plugins.

    This class is here for enabling us to run unit tests only,
    so most methods are simply stubs.
    """

    currentLayerChanged = pyqtSignal(QgsMapLayer)

    def __init__(self, canvas):
        """Constructor
        :param canvas:
        """
        QObject.__init__(self)
        self.canvas = canvas
        # Set up slots so we can mimic the behaviour of QGIS when layers
        # are added.
        LOGGER.debug("Initialising canvas...")
        QgsProject.instance().layersAdded.connect(self.addLayers)
        QgsProject.instance().layersRemoved.connect(self.removeAllLayers)

        # For processing module
        self.destCrs = None

    def addLayers(self, layers):  # QgsInterface override - camelCase required
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        current_layers = self.canvas.layers()
        final_layers = list(current_layers) + list(layers)
        self.canvas.setLayers(final_layers)

    def addLayer(self, layer):  # QgsInterface override - camelCase required
        """Handle a layer being added to the registry so it shows up in canvas.

        :param layer: list<QgsMapLayer> list of map layers that were added

        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.
        """
        pass

    def removeAllLayers(self):  # QgsInterface override - camelCase required
        """Remove layers from the canvas before they get deleted."""
        self.canvas.setLayers([])

    def newProject(self):  # QgsInterface override - camelCase required
        """Create new project."""
        QgsProject.instance().removeAllMapLayers()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):  # QgsInterface override - camelCase required
        """Zoom to the map full extent."""
        pass

    def zoomToPrevious(self):  # QgsInterface override - camelCase required
        """Zoom to previous view extent."""
        pass

    def zoomToNext(self):  # QgsInterface override - camelCase required
        """Zoom to next view extent."""
        pass

    def zoomToActiveLayer(self):  # QgsInterface override - camelCase required
        """Zoom to extent of active layer."""
        pass

    def addVectorLayer(self, path, base_name, provider_key):  # QgsInterface override
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        pass

    def addRasterLayer(self, path, base_name):  # QgsInterface override
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        pass

    def activeLayer(self):  # QgsInterface override - camelCase required
        """Get pointer to the active layer (layer selected in the legend)."""
        layers = QgsProject.instance().mapLayers()
        for item in layers:
            return layers[item]

    def addToolBarIcon(self, action):  # QgsInterface override - camelCase required
        """Add an icon to the plugins toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def removeToolBarIcon(self, action):  # QgsInterface override - camelCase required
        """Remove an action (icon) from the plugin toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def addToolBar(self, name):  # QgsInterface override - camelCase required
        """Add toolbar with specified name.

        :param name: Name for the toolbar.
        :type name: str
        """
        pass

    def mapCanvas(self):  # QgsInterface override - camelCase required
        """Return a pointer to the map canvas."""
        return self.canvas

    def mainWindow(self):  # QgsInterface override - camelCase required
        """Return a pointer to the main window.

        In case of QGIS it returns an instance of QgisApp.
        """
        pass

    def addDockWidget(self, area, dock_widget):  # QgsInterface override
        """Add a dock widget to the main window.

        :param area: Where in the ui the dock should be placed.
        :type area:

        :param dock_widget: A dock widget to add to the UI.
        :type dock_widget: QDockWidget
        """
        pass
