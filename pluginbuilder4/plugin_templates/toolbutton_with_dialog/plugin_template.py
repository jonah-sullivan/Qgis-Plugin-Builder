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

from pathlib import Path

from ...qgis_dirs import deployment_dir
from ..plugin_template import PluginTemplate


class ToolbuttonWithDialogPluginTemplate(PluginTemplate):
    def descr(self):
        return "Tool button with dialog"

    def subdir(self):
        return Path(__file__).parent

    def template_map(self, specification, dialog):
        menu_text = dialog.template_subframe.menu_text.text()
        menu = dialog.template_subframe.menu_location.currentText()
        # Munge the plugin menu function based on user choice
        if menu == "Plugins":
            add_method = "addPluginToMenu"
            remove_method = "removePluginMenu"
        else:
            add_method = f"addPluginTo{menu}Menu"
            remove_method = f"removePlugin{menu}Menu"
        self.category = menu
        m = specification.module_name
        ui_file = f"{m}_dialog_base.ui"
        return {
            # Makefile
            "TemplatePyFiles": f"{m}_dialog.py",
            "TemplateUiFiles": ui_file,
            "TemplateExtraFiles": "icon.png",
            "TemplateQGISDir": deployment_dir,
            # Metadata
            "TemplateHasProcessingProvider": False,
            # Menu
            "TemplateMenuText": menu_text,
            "TemplateMenuAddMethod": add_method,
            "TemplateMenuRemoveMethod": remove_method,
            # readme.tmpl extras
            "TemplateCompileResourcesStep": (
                "\n\n  * Compile the resources file using pyrcc6"
            ),
            "TemplateUiDesignerLine": (
                f"\n\n  * Create your own custom icon, replacing the default icon.png"
                f"\n\n  * Modify your user interface by opening {ui_file} in Qt Designer"  # noqa: E501
            ),
        }

    def template_files(self, specification):
        result = {
            "module_name_dialog.tmpl": f"{specification.module_name}_dialog.py",
            "module_name_dialog_base.ui.tmpl": f"{specification.module_name}_dialog_base.ui",
        }
        if specification.gen_tests:
            result.update(
                {
                    str(Path("test") / "test_module_name_dialog.templ"): str(Path("test") / "test_%s_dialog.py" % specification.module_name),
                    str(Path("test") / "test_resources.templ"): str(Path("test") / "test_resources.py"),
                }
            )
        return result

    def copy_files(self, specification):
        return {"icon.png": "icon.png"}
