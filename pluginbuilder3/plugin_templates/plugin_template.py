# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginTemplate
                                 A QGIS plugin
 plugin_template
                              -------------------
        begin                : 2015-03-17
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Pirmin Kalberer
        email                : pka@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


class PluginTemplate:
    """Base class for plugin templates."""

    def descr(self):
        raise NotImplementedError

    def subdir(self):
        raise NotImplementedError

    def template_map(self, specification, dialog):
        return {}

    def template_files(self, specification):
        return {}

    def copy_files(self, specification):
        return {}
