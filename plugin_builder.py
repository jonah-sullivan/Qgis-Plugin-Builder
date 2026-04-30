# coding=utf-8
"""
/***************************************************************************
    PluginBuilder
                                 A QGIS plugin
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

# Import Python stuff
import codecs
import configparser
import errno
import os
import shutil
from string import Template

from qgis.core import QgsApplication

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import QDir, QFile, QFileInfo, QSettings, QUrl
from qgis.PyQt.QtGui import (
    QDesktopServices,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox

# Import the code for the dialog
from .plugin_builder_dialog import PluginBuilderDialog
from .plugin_specification import PluginSpecification
from .result_dialog import ResultDialog
from .select_tags_dialog import SelectTagsDialog


class PluginBuilder:
    """A QGIS plugin that allows you to build QGIS plugins."""

    def __init__(self, iface):
        """Constructor

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface

        """
        # Save reference to the QGIS interface
        self.iface = iface
        # noinspection PyArgumentList
        self.user_plugin_dir = (
            QFileInfo(QgsApplication.qgisUserDatabaseFilePath()).path()
            + "/python/plugins"
        )
        self.plugin_builder_path = os.path.dirname(__file__)

        # class members
        self.action = None
        self.dialog = None
        self.plugin_path = None
        self.template = None
        self.shared_dir = None
        self.template_dir = None

    # noinspection PyPep8Naming
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(os.path.join(self.plugin_builder_path, "icon.png")),
            "Plugin Builder",
            self.iface.mainWindow(),
        )
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Plugin Builder", self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu("&Plugin Builder", self.action)
        self.iface.removeToolBarIcon(self.action)

    def _get_plugin_path(self):
        """Prompt the user for the path where the plugin should be written to."""
        while not QFileInfo(self.plugin_path).isWritable():
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.critical(None, "Error", "Directory is not writeable")
            # noinspection PyCallByClass,PyTypeChecker
            self.plugin_path = QFileDialog.getExistingDirectory(
                self.dialog,
                "Select the Directory for your Plugin",
                self._last_used_path(),
            )
            if self.plugin_path == "":
                return False
        return True

    def _prepare_tests(self, specification):
        """Populate and write test files."""
        test_source = os.path.join(self.shared_dir, "test")
        test_destination = os.path.join(self.plugin_path, "test")
        copy(test_source, test_destination)

        # Render lifecycle test for iface-based plugin types
        is_processing = specification.template_map.get(
            "TemplateHasProcessingProvider", False
        )
        if not is_processing:
            self.populate_template(
                specification,
                os.path.join(self.shared_dir),
                "test_plugin_lifecycle.tmpl",
                "test/test_plugin_lifecycle.py",
            )

        # Render pyproject.toml at plugin root
        self.populate_template(
            specification, self.shared_dir, "pyproject.toml.tmpl", "pyproject.toml"
        )

        # Copy requirements-dev.txt to plugin root
        QFile.copy(
            os.path.join(self.shared_dir, "requirements-dev.txt"),
            os.path.join(self.plugin_path, "requirements-dev.txt"),
        )

    def _prepare_scripts(self):
        """Copy the scripts folder."""
        scripts_source = os.path.join(self.shared_dir, "scripts")
        copy(scripts_source, os.path.join(self.plugin_path, "scripts"))

    def _prepare_i18n(self):
        """Copy the i18n folder."""
        scripts_source = os.path.join(self.shared_dir, "i18n")
        copy(scripts_source, os.path.join(self.plugin_path, "i18n"))

    def _prepare_help(self):
        """Prepare the help directory."""
        # Create sphinx default project for help
        QDir().mkdir(self.plugin_path + "/help")
        QDir().mkdir(self.plugin_path + "/help/build")
        QDir().mkdir(self.plugin_path + "/help/build/html")
        QDir().mkdir(self.plugin_path + "/help/source")
        QDir().mkdir(self.plugin_path + "/help/source/_static")
        QDir().mkdir(self.plugin_path + "/help/source/_templates")
        # copy doc makefiles
        # noinspection PyCallByClass,PyTypeChecker
        QFile.copy(
            os.path.join(self.shared_dir, "help/make.bat"),
            os.path.join(self.plugin_path, "help/make.bat"),
        )
        # noinspection PyCallByClass,PyTypeChecker
        QFile.copy(
            os.path.join(self.shared_dir, "help/Makefile"),
            os.path.join(self.plugin_path, "help/Makefile"),
        )

    def _prepare_code(self, specification):
        """Prepare the code turning templates into python.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification
        """
        # process the user entries
        if specification.gen_makefile:
            self.populate_template(
                specification, self.shared_dir, "Makefile.tmpl", "Makefile"
            )
        if specification.gen_pb_tool:
            self.populate_template(
                specification, self.shared_dir, "pb_tool.tmpl", "pb_tool.cfg"
            )
        self.populate_template(
            specification, self.template_dir, "__init__.tmpl", "__init__.py"
        )
        self.populate_template(
            specification,
            self.template_dir,
            "module_name.tmpl",
            "%s.py" % specification.module_name,
        )
        if specification.gen_scripts:
            release_script = QFile(os.path.join(self.shared_dir, "release.sh"))
            release_script.copy(os.path.join(self.plugin_path, "release.sh"))
            scripts_dir = os.path.join(self.plugin_path, "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            plugin_upload = QFile(os.path.join(self.shared_dir, "plugin_upload.py"))
            plugin_upload.copy(os.path.join(scripts_dir, "plugin_upload.py"))
            os.chmod(os.path.join(scripts_dir, "plugin_upload.py"), 0o755)  # nosec B103

    def _prepare_specific_files(self, specification):
        """Prepare specific templates and files.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification
        """
        for template_name, output_name in self.template.template_files(
            specification
        ).items():
            self.populate_template(
                specification, self.template_dir, template_name, output_name
            )

        # copy the non-generated files to the new plugin dir
        for template_file, output_name in self.template.copy_files(
            specification
        ).items():
            t_file = QFile(os.path.join(self.template_dir, template_file))
            t_file.copy(os.path.join(self.plugin_path, output_name))

    def _prepare_readme(self, specification, template_module_name):
        """Prepare the README file.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification

        :param template_module_name: Base name of the module for the new
            plugin.
        :type template_module_name: str
        """
        # populate the results readme text template
        template_file = open(os.path.join(self.template_dir, "readme.tmpl"))
        content = template_file.read()
        template_file.close()
        template = Template(content)
        # TODO: update this to simply pass the specification.template_map
        result_map = {
            "PluginDir": self.plugin_path,
            "TemplateClass": specification.template_map["TemplateClass"],
            "TemplateModuleName": template_module_name,
            "UserPluginDir": self.user_plugin_dir,
            "TemplateVCSFormat": specification.template_map["TemplateVCSFormat"],
        }
        popped = template.safe_substitute(result_map)
        # write the results info to the README txt file
        readme_txt = codecs.open(
            os.path.join(str(self.plugin_path), "README.txt"), "w", "utf-8"
        )
        readme_txt.write(popped)
        readme_txt.close()

    def _prepare_metadata(self, specification):
        """Prepare metadata file.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification
        """
        processing_provider = specification.template_map[
            "TemplateHasProcessingProvider"
        ]
        metadata_file = codecs.open(
            os.path.join(str(self.plugin_path), "metadata.txt"), "w", "utf-8"
        )
        metadata_comment = (
            "# This file contains metadata for your plugin.\n\n"
            "# This file should be included when you package your plugin.\n"
            "# Mandatory items:\n\n"
        )
        metadata_file.write(metadata_comment)
        metadata_file.write("[general]\n")
        metadata_file.write("name=%s\n" % specification.title)
        metadata_file.write(
            "qgisMinimumVersion=%s\n" % specification.qgis_minimum_version
        )
        metadata_file.write(
            "qgisMaximumVersion=%s\n" % specification.qgis_maximum_version
        )
        metadata_file.write("description=%s\n" % specification.description)
        metadata_file.write("version=%s\n" % specification.plugin_version)
        metadata_file.write("author=%s\n" % specification.author)
        metadata_file.write("email=%s\n\n" % specification.email_address)
        metadata_file.write("about=%s\n\n" % specification.about)
        metadata_file.write("tracker=%s\n" % specification.tracker)
        metadata_file.write("repository=%s\n" % specification.repository)
        metadata_file.write("license=GNU GPL v2\n")
        metadata_file.write("# End of mandatory metadata\n\n")
        metadata_file.write("# Recommended items:\n\n")
        metadata_file.write(
            "hasProcessingProvider={}\n".format("yes" if processing_provider else "no")
        )
        metadata_file.write("# Uncomment the following line and add your changelog:\n")
        metadata_file.write("# changelog=\n\n")
        metadata_file.write("# Tags are comma separated with spaces allowed\n")
        metadata_file.write("tags=%s\n\n" % specification.tags)
        metadata_file.write("homepage=%s\n" % specification.homepage)
        metadata_file.write("category=%s\n" % self.template.category)
        metadata_file.write("icon=%s\n" % specification.icon)
        metadata_file.write("# experimental flag\n")
        metadata_file.write("experimental=%s\n\n" % specification.experimental)
        metadata_file.write(
            "# deprecated flag (applies to the whole plugin, not "
            "just a single version)\n"
        )
        metadata_file.write("deprecated=%s\n\n" % specification.deprecated)
        metadata_file.write(
            "# Since QGIS 3.8, a comma separated list of plugins to be " "installed\n"
        )
        metadata_file.write("# (or upgraded) can be specified.\n")
        metadata_file.write("# Check the documentation for more information.\n")
        metadata_file.write("# plugin_dependencies=\n\n")
        metadata_file.write("# Category of the plugin: Raster, Vector, Database or Web\n")
        metadata_file.write("# category=\n\n")
        metadata_file.write("# If the plugin can run on QGIS Server.\n")
        metadata_file.write("server=False\n\n")
        metadata_file.close()

    def _prepare_results_html(self, specification):
        """Prepare results README.html file.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification
        """
        template_module_name = specification.template_map["TemplateModuleName"]
        template_file = open(os.path.join(self.template_dir, "results.tmpl"))
        content = template_file.read()
        template_file.close()
        template = Template(content)
        result_map = {
            "PluginDir": self.plugin_path,
            "TemplateClass": specification.template_map["TemplateClass"],
            "TemplateModuleName": template_module_name,
            "UserPluginDir": self.user_plugin_dir,
            "TemplateVCSFormat": specification.template_map["TemplateVCSFormat"],
        }
        results_popped = template.safe_substitute(result_map)
        # write the results info to the README HTML file
        readme = codecs.open(
            os.path.join(str(self.plugin_path), "README.html"), "w", "utf-8"
        )
        readme.write(results_popped)
        readme.close()
        return results_popped, template_module_name

    def _create_plugin_directory(self):
        """Create the plugin directory using the module name."""
        self.plugin_path = os.path.join(
            str(self.plugin_path), str(self.dialog.module_name.text().lower())
        )
        QDir().mkdir(self.plugin_path)

    def _last_used_path(self):
        """Return the last used plugin path from settings"""
        return QSettings().value("PluginBuilder/last_path", ".")

    def _set_last_used_path(self, value):
        """Set the last used plugin path for future use"""
        QSettings().setValue("PluginBuilder/last_path", value)

    def _select_tags(self):
        """Select tags for the new plugin from the tags dialog"""
        tag_dialog = SelectTagsDialog()
        # if the user has their own taglist, use it
        user_tag_list = os.path.join(os.path.expanduser("~"), ".plugin_tags.txt")
        if os.path.exists(user_tag_list):
            tag_file = user_tag_list
        else:
            tag_file = os.path.join(str(self.plugin_builder_path), "taglist.txt")

        with open(tag_file) as tf:
            tags = tf.readlines()

        model = QStandardItemModel()

        for tag in tags:
            item = QStandardItem(tag[:-1])
            model.appendRow(item)

        tag_dialog.listView.setModel(model)
        tag_dialog.show()
        ok = tag_dialog.exec()
        if ok:
            selected = tag_dialog.listView.selectedIndexes()
            seltags = []
            for tag in selected:
                seltags.append(tag.data())
            taglist = ", ".join(seltags)
            self.dialog.tags.setText(taglist)
        # QMessageBox.information(None, "Selection", seltags)

    def run(self):
        """Run method that performs all the real work"""
        # create and show the dialog
        self.dialog = PluginBuilderDialog(stored_output_path=self._last_used_path())

        # get version
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(self.plugin_builder_path, "metadata.txt"))
        version = cfg.get("general", "version")
        self.dialog.setWindowTitle("QGIS Plugin Builder - {}".format(version))

        # connect the ok button to our method
        self.dialog.button_box.helpRequested.connect(self.show_help)
        self.dialog.select_tags.clicked.connect(self._select_tags)

        # show the dialog
        self.dialog.show()
        self.dialog.adjustSize()
        result = self.dialog.exec()
        if not result:
            return

        specification = PluginSpecification(self.dialog)
        # get the location for the plugin
        # noinspection PyCallByClass,PyTypeChecker
        self.plugin_path = self.dialog.output_directory.text()

        self._set_last_used_path(self.plugin_path)
        self._create_plugin_directory()
        self.template = self.dialog.template()
        self.template_dir = os.path.join(self.template.subdir(), "template")
        self.shared_dir = os.path.join(
            str(self.plugin_builder_path), "plugin_templates", "shared"
        )

        template_map = self.template.template_map(specification, self.dialog)
        specification.template_map.update(template_map)

        deps = []
        if specification.gen_i18n:
            deps.append("transcompile")
        test_deps = " ".join(deps)
        if specification.gen_help:
            deps.append("doc")
        deploy_deps = " ".join(deps)
        specification.template_map["TemplateTestDeps"] = test_deps
        specification.template_map["TemplateDeployDeps"] = deploy_deps
        specification.template_map["TemplateDeployCopyI18n"] = (
            "\tcp -vfr i18n $(QGISDIR)/$(PLUGINNAME)" if specification.gen_i18n else ""
        )
        specification.template_map["TemplateDeployCopyHelp"] = (
            "\tcp -vfr $(HELP) $(QGISDIR)/$(PLUGINNAME)/help"
            if specification.gen_help
            else ""
        )

        self._prepare_code(specification)
        if specification.gen_help:
            self._prepare_help()
            # create the sphinx config file and sample index.rst file
            self.populate_template(
                specification,
                self.shared_dir,
                "help/source/conf.py.tmpl",
                "help/source/conf.py",
            )
            self.populate_template(
                specification,
                self.shared_dir,
                "help/source/index.rst.tmpl",
                "help/source/index.rst",
            )
        if specification.gen_tests:
            self._prepare_tests(specification)

        if specification.gen_scripts:
            self._prepare_scripts()

        if specification.gen_i18n:
            self._prepare_i18n()

        self._prepare_specific_files(specification)

        results_popped, template_module_name = self._prepare_results_html(specification)

        self._prepare_readme(specification, template_module_name)
        self._prepare_metadata(specification)

        # show the results
        results_dialog = ResultDialog()
        results_dialog.web_view.setHtml(results_popped)
        results_dialog.show()
        results_dialog.exec()

    def populate_template(
        self, specification, template_dir, template_name, output_name
    ):
        """Populate the template based on user data.

        :param specification: Descriptive data that will be used to create
            the plugin.
        :type specification: PluginSpecification

        :param template_dir: Directory where template is.
        :type template_dir: str

        :param template_name: Name for the template.
        :type template_name: str

        :param output_name:  Name of the output file to create.
        :type output_name: str
        """
        template_file_path = os.path.join(template_dir, template_name)
        output_name_path = os.path.join(self.plugin_path, output_name)

        template_file = open(template_file_path)
        content = template_file.read()
        template_file.close()
        template = Template(content)
        popped = template.safe_substitute(specification.template_map)
        plugin_file = codecs.open(output_name_path, "w", "utf-8")
        plugin_file.write(popped)
        plugin_file.close()

    def show_help(self):
        """Display application help to the user."""
        help_file = os.path.join(self.plugin_builder_path, "help", "index.html")
        if os.path.exists(help_file):
            QDesktopServices.openUrl(QUrl("file:///" + help_file))
        else:
            QDesktopServices.openUrl(
                QUrl("https://jonah-sullivan.github.io/Qgis-Plugin-Builder/")
            )


def copy(source, destination):
    """Copy files recursively.

    Taken from: http://www.pythoncentral.io/
                how-to-recursively-copy-a-directory-folder-in-python/

    :param source: Source directory.
    :type source: str

    :param destination: Destination directory.
    :type destination: str

    """
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(source, destination)
        else:
            print("Directory not copied. Error: %s" % e)
