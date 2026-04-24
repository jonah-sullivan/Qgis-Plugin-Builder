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
from ..plugin_template import PluginTemplate
from ...qgis_dirs import deployment_dir


class ProcessingProviderPluginTemplate(PluginTemplate):

    def descr(self):
        return "Processing Provider"

    def subdir(self):
        return os.path.dirname(__file__)

    def template_map(self, specification, dialog):
        self.category = 'Analysis'
        frame = dialog.template_subframe
        return {
            # Makefile
            'TemplateQGISDir': deployment_dir,
            # Metadata
            'TemplateHasProcessingProvider': True,
            # Processing
            'TemplateAlgoName': frame.algo_name_text.text(),
            'TemplateAlgoGroup': frame.algo_group_text.text(),
            'TemplateProviderName': frame.provider_name_text.text(),
            'TemplateProviderDescr': frame.provider_descr_text.text()
        }

    def template_files(self, specification):
        return {
            'module_name_algorithm.tmpl':
            '%s_algorithm.py' % specification.module_name,
            'module_name_provider.tmpl':
            '%s_provider.py' % specification.module_name,
        }
