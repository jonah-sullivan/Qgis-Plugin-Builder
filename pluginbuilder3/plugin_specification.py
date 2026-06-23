# coding=utf-8
"""
/***************************************************************************
    PluginSpec

    Creates a skeleton QGIS plugin for use as a starting point
                             -------------------
        begin                : 2011-01-20
        git sha              : $Format:%H$
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
"""
import datetime


class PluginSpecification:
    """A convenience store with information needed to create the plugin."""
    def __init__(self, dialog):
        """Constructor.

        After calling the constructor, the class properties
        self.template_map, self.experimental etc. will be set.

        :param dialog: A plugin builder dialog with populated options.
        :type dialog: PluginBuilderDialog

        """
        self.class_name = str(dialog.class_name.text())
        self.author = dialog.author.text()
        self.description = dialog.description.text()
        self.module_name = dialog.module_name.text()
        self.email_address = dialog.email_address.text()
        self.qgis_minimum_version = dialog.qgis_minimum_version.text()
        self.title = dialog.title.text()
        self.plugin_version = dialog.plugin_version.text()

        # remove multiple newlines/spaces from about text
        about = dialog.about.toPlainText().replace('\n', ' ')
        self.about = ' '.join(about.split())

        self.homepage = dialog.homepage.text()
        self.tracker = dialog.tracker.text()
        self.repository = dialog.repository.text()
        self.tags = dialog.tags.text()
        # icon selection from disk will be added at a later version
        self.icon = 'icon.png'
        self.experimental = dialog.experimental.isChecked()
        # deprecated is always false for a new plugin
        self.deprecated = False
        # Builder flags
        self.gen_i18n = dialog.i18n_cb.isChecked()
        self.gen_help = dialog.help_cb.isChecked()
        self.gen_tests = dialog.tests_cb.isChecked()
        self.gen_scripts = dialog.scripts_cb.isChecked()
        self.gen_makefile = dialog.makefile_cb.isChecked()
        self.gen_pb_tool = dialog.pb_tool_cb.isChecked()
        # Add the date stuff to the template map
        now = datetime.date.today()
        self.build_year = now.year
        self.build_date = '%i-%02i-%02i' % (now.year, now.month, now.day)
        # Git will replace this with the sha - I do it a funny way below so
        # that this line below does not itself get substituted by git!
        self.vcs_format = '$Format:' + '%H$'
        self.template_map = {
            'TemplateClass': self.class_name,
            'TemplateTitle': self.title,
            'TemplateDescription': self.description,
            'TemplateModuleName': self.module_name,
            'TemplateVersion': self.plugin_version,
            'TemplateQgisVersion': self.qgis_minimum_version,
            'TemplateAuthor': self.author,
            'TemplateEmail': self.email_address,
            'PluginDirectoryName': self.class_name.lower(),
            'TemplateBuildDate': self.build_date,
            'TemplateYear': self.build_year,
            'TemplateVCSFormat': self.vcs_format,
            # Makefile defaults
            'TemplatePyFiles': '',
            'TemplateUiFiles': '',
            'TemplateExtraFiles': '',
            'TemplateQrcFiles': '',
            'TemplateRcFiles': ''
        }
