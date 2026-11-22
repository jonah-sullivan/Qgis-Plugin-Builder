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

if TYPE_CHECKING:
    from ..plugin_builder_dialog import PluginBuilderDialog
    from ..plugin_specification import PluginSpecification, TemplateMap


class PluginTemplate:
    """Base class for plugin templates.

    Each plugin type the wizard offers (tool button with dialog, tool button
    with dock widget, Processing provider) is a subclass in its own folder.
    To add a new type, create a subclass and add it to templates() in
    plugin_templates/__init__.py.
    """

    # Plugin category for metadata.txt. Subclasses must set this in
    # template_map(), which runs before metadata.txt is written; if it is
    # never set, generation fails with an AttributeError.
    category: str

    def descr(self) -> str:
        """Return the label shown for this template in the wizard's drop-down."""
        raise NotImplementedError

    def subdir(self) -> Path:
        """Return this template's folder.

        It must contain a template/ folder with the files to render or copy,
        and wizard_form_base.ui, the template's extra options on the
        wizard's template page.
        """
        raise NotImplementedError

    def template_map(
        self, specification: "PluginSpecification", dialog: "PluginBuilderDialog"
    ) -> "TemplateMap":
        """Return extra placeholder values specific to this template type.

        The keys are placeholder names used in this template's .tmpl files
        (TemplateMenuText for the $TemplateMenuText placeholder, say). They
        are merged into the shared values from PluginSpecification.template_map.
        Subclasses must also set self.category here.

        :param specification: The user's choices from the wizard.
        :param dialog: The wizard, for reading this template's own options
            from dialog.template_subframe.
        """
        return {}

    def template_files(self, specification: "PluginSpecification") -> dict[str, str]:
        """Map .tmpl files to the output files rendered from them.

        Placeholders are filled in during rendering. Keys are relative to
        subdir() / "template"; values are relative to the new plugin's root
        folder.
        """
        return {}

    def copy_files(self, specification: "PluginSpecification") -> dict[str, str]:
        """Map files to copy unchanged, such as icon.png.

        Paths are relative in the same way as for template_files().
        """
        return {}

    def what_next_items_html(
        self, plugin_path: Path, module_name: str, ui_file: str
    ) -> str:
        """Return the "what next" steps shown in the results dialog.

        :param plugin_path: Folder the plugin was generated into.
        :param module_name: The plugin's module name.
        :param ui_file: The plugin's Qt Designer .ui file name, if it has one.
        :returns: HTML <li> items, inserted into a list in results.tmpl.
        """
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
