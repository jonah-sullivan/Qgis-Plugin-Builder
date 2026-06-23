# coding=utf-8
"""
/***************************************************************************
    PluginBuilder

    Creates a QGIS plugin template for use as a starting point in plugin
    development.
                             -------------------
        begin                : 2011-01-20
        copyright            : (C) 2011-2014 by GeoApt LLC
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


# pylint: disable=C0103
# noinspection PyPep8Naming
def classFactory(iface):
    """Load PluginBuilder class from file PluginBuilder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .plugin_builder import PluginBuilder
    return PluginBuilder(iface)
# pylint: enable=C0103
