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

import os

from ...qgis_dirs import deployment_dir
from ..plugin_template import PluginTemplate


class ToolbuttonWithDockWidgetPluginTemplate(PluginTemplate):

    def descr(self):
        return "Tool button with dock widget"

    def subdir(self):
        return os.path.dirname(__file__)

    def template_map(self, specification, dialog):
        menu_text = dialog.template_subframe.menu_text.text()
        menu = dialog.template_subframe.menu_location.currentText()
        # Munge the plugin menu function based on user choice
        if menu == "Plugins":
            add_method = "addPluginToMenu"
            remove_method = "removePluginMenu"
        else:
            add_method = "addPluginTo{}Menu".format(menu)
            remove_method = "removePlugin{}Menu".format(menu)
        self.category = menu

        dockwidget_area = dialog.template_subframe.dockwidget_area.currentText()
        
        # Map dock widget area names to Qt.DockWidgetArea enum values
        dock_area_map = {
            "Left": "Qt.DockWidgetArea.LeftDockWidgetArea",
            "Right": "Qt.DockWidgetArea.RightDockWidgetArea",
            "Top": "Qt.DockWidgetArea.TopDockWidgetArea",
            "Bottom": "Qt.DockWidgetArea.BottomDockWidgetArea",
        }

        return {
            # Makefile
            "TemplatePyFiles": "%s_dockwidget.py" % specification.module_name,
            "TemplateUiFiles": "%s_dockwidget_base.ui" % specification.module_name,
            "TemplateExtraFiles": "icon.png",
            "TemplateQGISDir": deployment_dir,
            # Metadata
            "TemplateHasProcessingProvider": False,
            # Menu
            "TemplateMenuText": menu_text,
            "TemplateMenuAddMethod": add_method,
            "TemplateMenuRemoveMethod": remove_method,
            # DockWidget
            "TemplateDockWidgetArea": dock_area_map[dockwidget_area],
        }

    def template_files(self, specification):
        result = {
            "module_name_dockwidget.tmpl": "%s_dockwidget.py"
            % specification.module_name,
            "module_name_dockwidget_base.ui.tmpl": "%s_dockwidget_base.ui"
            % specification.module_name,
        }
        if specification.gen_tests:
            result.update(
                {
                    os.path.join("test", "test_module_name_dockwidget.templ"): (
                        os.path.join("test", "test_%s_dockwidget.py" % specification.module_name)
                    ),
                    os.path.join("test", "test_resources.templ"): os.path.join("test", "test_resources.py"),
                }
            )
        return result

    def copy_files(self, specification):
        return {"icon.png": "icon.png"}
