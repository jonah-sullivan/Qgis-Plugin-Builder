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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..plugin_builder_dialog import PluginBuilderDialog
    from ..plugin_specification import PluginSpecification, TemplateMap


class PluginTemplate:
    """Base class for plugin templates."""

    # Plugin category for metadata.txt; set by template_map()
    category: str

    def descr(self) -> str:
        raise NotImplementedError

    def subdir(self) -> str:
        raise NotImplementedError

    def template_map(
        self, specification: "PluginSpecification", dialog: "PluginBuilderDialog"
    ) -> "TemplateMap":
        return {}

    def template_files(self, specification: "PluginSpecification") -> dict[str, str]:
        return {}

    def copy_files(self, specification: "PluginSpecification") -> dict[str, str]:
        return {}

    def what_next_items_html(
        self, plugin_path: str, module_name: str, ui_file: str
    ) -> str:
        return (
            f"    <li>Test the plugin by enabling it in the QGIS plugin manager\n"
            f"    <li>Customize it by editing the implementation file"
            f" <b>{module_name}.py</b>\n"
            f"    <li>Create your own custom icon, replacing the default"
            f" <b>icon.png</b>\n"
            f"    <li>Modify your user interface by opening"
            f' <a href="file:///{plugin_path}/{ui_file}"><b>{ui_file}</b></a>'
            f" in Qt Designer"
        )
