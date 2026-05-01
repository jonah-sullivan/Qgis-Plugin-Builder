# coding=utf-8
"""Common functionality used by regression tests."""

import logging
import os
import sys

LOGGER = logging.getLogger("QGIS")
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None


def get_qgis_app():
    """Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas
        from qgis.PyQt import QtCore, QtWidgets

        from .qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP
    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        argv = [a.encode() for a in sys.argv]
        QGIS_APP = QgsApplication(argv, gui_flag)
        prefix_path = os.environ.get("QGIS_PREFIX_PATH", "/usr")
        QgsApplication.setPrefixPath(prefix_path, True)
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    global PARENT
    if PARENT is None:
        PARENT = QtWidgets.QWidget()

    global CANVAS
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT
