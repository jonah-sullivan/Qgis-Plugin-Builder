# coding=utf-8
"""Utilities for testing.

Note: Shameless duplication exists here with what is in the
template plugin file structure. Figure out how to have DRY.

Tim Sutton
"""

import getpass
import logging
import os
import sys
from datetime import date
from tempfile import mkstemp

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
        from qgis.PyQt import QtCore, QtGui

        from .qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP
    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        QGIS_APP = QgsApplication(sys.argv, gui_flag)
        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    global PARENT
    if PARENT is None:
        PARENT = QtGui.QWidget()

    global CANVAS
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


def temp_dir(sub_dir="work"):
    """Obtain the temporary working directory for the operating system.

    .. note:: Taken from InaSAFE:
         https://github.com/AIFDR/inasafe/blob/master/safe/common/utilities.py

    An inasafe subdirectory will automatically be created under this and
    if specified, a user subdirectory under that.

    .. note:: You can use this together with unique_filename to create
       a file in a temporary directory under the inasafe workspace. e.g.

       tmpdir = temp_dir('testing')
       tmpfile = unique_filename(dir=tmpdir)
       print tmpfile
       /tmp/inasafe/23-08-2012/timlinux/testing/tmpMRpF_C

    If you specify INASAFE_WORK_DIR as an environment var, it will be
    used in preference to the system temp directory.

    :param sub_dir: Optional argument which will cause an additional
        subdirectory to be created e.g. /tmp/inasafe/foo/
    :type sub_dir: str

    :return: Path to the output clipped layer (placed in the system temp dir).
    :rtype: str

    :raises: Any errors from the underlying system calls.
    """
    user = getpass.getuser().replace(" ", "_")
    current_date = date.today()
    date_string = current_date.isoformat()

    # Following 4 lines are a workaround for tempfile.tempdir() unreliabilty
    handle, filename = mkstemp()
    os.close(handle)
    new_directory = os.path.dirname(filename)
    os.remove(filename)

    path = os.path.join(new_directory, "pluginbuilder", date_string, user, sub_dir)

    if not os.path.exists(path):
        # Ensure that the dir is world writable
        # Umask sets the new mask and returns the old
        old_mask = os.umask(0000)
        os.makedirs(path, 0o777)
        # Reinstate the old mask for tmp
        os.umask(old_mask)
    return path


def unique_filename(**kwargs):
    """Create new filename guaranteed not to exist previously

    Use mkstemp to create the file, then remove it and return the name

    If dir is specified, the tempfile will be created in the path specified
    otherwise the file will be created in a directory following this scheme:

    :file:'/tmp/inasafe/<dd-mm-yyyy>/<user>/impacts'

    See http://docs.python.org/library/tempfile.html for details.

    Example usage:

    tempdir = temp_dir(sub_dir='test')
    filename = unique_filename(suffix='.keywords', dir=tempdir)
    print filename
    /tmp/inasafe/23-08-2012/timlinux/test/tmpyeO5VR.keywords

    Or with no preferred subdir, a default subdir of 'impacts' is used:

    filename = unique_filename(suffix='.shp')
    print filename
    /tmp/inasafe/23-08-2012/timlinux/impacts/tmpoOAmOi.shp

    :param kwargs: Keyword arguments.
    :type kwargs: dict

    """

    if "dir" not in kwargs:
        path = temp_dir("impacts")
        kwargs["dir"] = path
    else:
        path = temp_dir(kwargs["dir"])
        kwargs["dir"] = path
    if not os.path.exists(kwargs["dir"]):
        # Ensure that the dir mask won't conflict with the mode
        # Umask sets the new mask and returns the old
        umask = os.umask(0000)
        # Ensure that the dir is world writable by explicitly setting mode
        os.makedirs(kwargs["dir"], 0o777)
        # Reinstate the old mask for tmp dir
        os.umask(umask)
    # Now we have the working dir set up go on and return the filename
    handle, filename = mkstemp(**kwargs)

    # Need to close it using the file handle first for windows!
    os.close(handle)
    try:
        os.remove(filename)
    except OSError:
        pass
    return filename
