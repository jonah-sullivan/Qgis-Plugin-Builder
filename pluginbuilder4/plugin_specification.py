# coding=utf-8
"""
/***************************************************************************
    PluginSpec

    Creates a skeleton QGIS plugin for use as a starting point
                             -------------------
        begin                : 2011-01-20
        git sha              : $Format:%H$
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
"""

import datetime
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .plugin_builder_dialog import PluginBuilderDialog

# Substitution values for string.Template placeholders in the plugin templates
TemplateMap: TypeAlias = dict[str, str | int | bool]


class PluginSpecification:
    """A convenience store with information needed to create the plugin."""

    def __init__(self, dialog: "PluginBuilderDialog") -> None:
        """Constructor.

        After calling the constructor, the class properties
        self.template_map, self.experimental etc. will be set.

        :param dialog: A plugin builder dialog with populated options.
        :type dialog: PluginBuilderDialog

        """
        self.class_name: str = str(dialog.class_name.text())
        self.author: str = dialog.author.text()
        self.description: str = dialog.description.text()
        self.module_name: str = dialog.module_name.text()
        self.email_address: str = dialog.email_address.text()
        self.qgis_minimum_version: str = dialog.qgis_minimum_version.text()
        self.qgis_maximum_version: str = dialog.qgis_maximum_version.text()
        self.title: str = dialog.title.text()
        self.plugin_version: str = dialog.plugin_version.text()

        # remove multiple newlines/spaces from about text
        about = dialog.about.toPlainText().replace("\n", " ")
        self.about = " ".join(about.split())

        self.homepage: str = dialog.homepage.text()
        self.tracker: str = dialog.tracker.text()
        self.repository: str = dialog.repository.text()
        self.tags: str = dialog.tags.text()
        # icon selection from disk will be added at a later version
        self.icon = "icon.png"
        self.experimental: bool = dialog.experimental.isChecked()
        # deprecated is always false for a new plugin
        self.deprecated = False
        # Builder flags
        self.gen_i18n: bool = dialog.i18n_cb.isChecked()
        self.gen_help: bool = dialog.help_cb.isChecked()
        self.gen_tests: bool = dialog.tests_cb.isChecked()
        self.gen_makefile: bool = dialog.makefile_cb.isChecked()
        self.gen_pb_tool: bool = dialog.pb_tool_cb.isChecked()
        self.gen_qgis_plugin_ci: bool = dialog.qgis_plugin_ci_cb.isChecked()
        self.gen_gitlab_ci: bool = dialog.gitlab_ci_cb.isChecked()
        self.github_org_slug: str = (
            dialog.github_org_slug.text().strip() if self.gen_qgis_plugin_ci else ""
        )
        self.gitlab_namespace: str = (
            dialog.gitlab_namespace.text().strip() if self.gen_gitlab_ci else ""
        )
        self.project_slug: str = (
            dialog.project_slug.text().strip()
            if (self.gen_qgis_plugin_ci or self.gen_gitlab_ci)
            else ""
        )
        # Add the date stuff to the template map
        now = datetime.date.today()
        self.build_year = now.year
        self.build_date = "%i-%02i-%02i" % (now.year, now.month, now.day)
        # Git will replace this with the sha - I do it a funny way below so
        # that this line below does not itself get substituted by git!
        self.vcs_format = "$Format:" + "%H$"
        self.template_map: TemplateMap = {
            "TemplateClass": self.class_name,
            "TemplateTitle": self.title,
            "TemplateDescription": self.description,
            "TemplateModuleName": self.module_name,
            "TemplateVersion": self.plugin_version,
            "TemplateQgisMinVersion": self.qgis_minimum_version,
            "TemplateQgisMaxVersion": self.qgis_maximum_version,
            "TemplateAuthor": self.author,
            "TemplateEmail": self.email_address,
            "PluginDirectoryName": self.class_name.lower(),
            "TemplateBuildDate": self.build_date,
            "TemplateYear": self.build_year,
            "TemplateVCSFormat": self.vcs_format,
            # Makefile defaults
            "TemplatePyFiles": "",
            "TemplateUiFiles": "",
            "TemplateExtraFiles": "",
            "TemplateQrcFiles": "",
            "TemplateRcFiles": "",
            # readme.tmpl template-specific lines (overridden by each template)
            "TemplateCompileResourcesStep": "",
            "TemplateUiDesignerLine": "",
            # qgis-plugin-ci (populated at generation time)
            "TemplateGitHubOrg": self.github_org_slug,
            "TemplateGitLabNamespace": self.gitlab_namespace,
            "TemplateProjectSlug": self.project_slug,
            "TemplateQgisPluginCiSteps": "",
        }
