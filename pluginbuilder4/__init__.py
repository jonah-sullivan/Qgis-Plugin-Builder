"""
/***************************************************************************
    PluginBuilder

    Creates a QGIS plugin template for use as a starting point in plugin
    development.
                             -------------------
        begin                : 2011-01-20
        copyright            : (C) 2011-2026 by Gary Sherman, 2026 Jonah Sullivan
        email                : gsherman@geoapt.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

    from .plugin_builder import PluginBuilder


def classFactory(iface: "QgisInterface") -> "PluginBuilder":
    """Entry point that QGIS calls to load this plugin.

    QGIS looks for a function with exactly this name in the plugin's
    __init__.py. It must return an object with initGui() and unload() methods.

    :param iface: The QGIS interface: the plugin's handle on the main window,
        map canvas, menus and toolbars.
    :type iface: QgisInterface
    """
    from .plugin_builder import PluginBuilder

    return PluginBuilder(iface)
