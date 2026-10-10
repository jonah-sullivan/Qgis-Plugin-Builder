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
from typing import TYPE_CHECKING

from ...qgis_dirs import deployment_dir
from ..plugin_template import PluginTemplate

if TYPE_CHECKING:
    from ...plugin_builder_dialog import PluginBuilderDialog
    from ...plugin_specification import PluginSpecification, TemplateMap


class ProcessingProviderPluginTemplate(PluginTemplate):
    def descr(self) -> str:
        return "Processing Provider"

    def subdir(self) -> Path:
        return Path(__file__).parent

    def template_map(
        self, specification: "PluginSpecification", dialog: "PluginBuilderDialog"
    ) -> "TemplateMap":
        self.category = "Analysis"
        # template_subframe is built from this template's wizard_form_base.ui
        frame = dialog.template_subframe
        algo_name: str = frame.algo_name_text.text()
        algo_group: str = frame.algo_group_text.text()
        provider_name: str = frame.provider_name_text.text()
        provider_descr: str = frame.provider_descr_text.text()
        return {
            # Makefile
            "TemplateQGISDir": str(deployment_dir),
            "TemplatePyFiles": "%s_algorithm.py %s_provider.py"
            % (specification.module_name, specification.module_name),
            # Metadata
            "TemplateHasProcessingProvider": True,
            # Processing
            "TemplateAlgoName": algo_name,
            "TemplateAlgoGroup": algo_group,
            "TemplateProviderName": provider_name,
            "TemplateProviderDescr": provider_descr,
        }

    def what_next_items_html(
        self, plugin_path: Path, module_name: str, ui_file: str
    ) -> str:
        algo_file = f"{module_name}_algorithm.py"
        return (
            f"    <li>Test the plugin by enabling it in the QGIS plugin manager"
            f" and enabling the provider in the Processing Options\n"
            f"    <li>Customize it by editing the implementation file"
            f' <a href="file:///{plugin_path}/{algo_file}"><b>{algo_file}</b></a>'
        )

    def template_files(self, specification: "PluginSpecification") -> dict[str, str]:
        files = {
            "module_name_algorithm.tmpl": "%s_algorithm.py" % specification.module_name,
            "module_name_provider.tmpl": "%s_provider.py" % specification.module_name,
        }
        if specification.gen_tests:
            files[str(Path("test") / "test_plugin_lifecycle.templ")] = str(
                Path("test") / "test_plugin_lifecycle.py"
            )
        return files
