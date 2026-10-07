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
import configparser
import errno
from pathlib import Path
import shutil
from string import Template

from qgis.core import QgsApplication

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QDir,
    QFile,
    QFileInfo,
    QLocale,
    QSettings,
    QTranslator,
    QUrl,
)
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

    def tr(self, message):
        return QCoreApplication.translate("PluginBuilder", message)

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
        self.plugin_builder_path = Path(__file__).parent

        locale = QLocale(QgsApplication.locale())
        locale_path = self.plugin_builder_path / "i18n" / "{}.qm".format(locale.name()[:2])
        if locale_path.exists():
            self.translator = QTranslator()
            self.translator.load(str(locale_path))
            QCoreApplication.installTranslator(self.translator)

        # class members
        self.action = None
        self.menu = None
        self.dialog = None
        self.plugin_path: Path = Path()
        self.template = None
        self.shared_dir: Path = Path()
        self.template_dir = None

    def initGui(self):  # QGIS API override - camelCase required
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon = QIcon(self.plugin_builder_path / "icon.png")
        self.menu = self.iface.pluginMenu().addMenu(icon, self.tr("&Plugin Builder"))
        self.action = QAction(
            icon,
            self.tr("Plugin Builder"),
            self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)
        self.menu.addAction(self.action)

        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.pluginMenu().removeAction(self.menu.menuAction())
        self.iface.removeToolBarIcon(self.action)

    def _get_plugin_path(self):
        """Prompt the user for the path where the plugin should be written to."""
        while not QFileInfo(str(self.plugin_path)).isWritable():
            # noinspection PyTypeChecker,PyArgumentList
            QMessageBox.critical(
                None, self.tr("Error"), self.tr("Directory is not writeable")
            )
            self.plugin_path = Path(QFileDialog.getExistingDirectory(
                self.dialog,
                self.tr("Select the Directory for your Plugin"),
                str(self._last_used_path()),
            ))
            if self.plugin_path == "":
                return False
        return True

    def _prepare_tests(self, specification):
        """Populate and write test files."""
        test_source = self.shared_dir / "test"
        test_destination = Path(self.plugin_path) / "test"
        copy(str(test_source), str(test_destination))

        # Templates that use `assert` are stored as .tmpl so Bandit's B101
        # rule doesn't flag Plugin Builder's own packaged .py files when it
        # is scanned for upload; restore the .py extension here.
        for entry in test_destination.iterdir():
            if entry.suffix == ".tmpl":
                Path(test_destination / entry).replace(test_destination / entry.with_suffix(".py"))

        # Exclude test/ from packaged zips (tests use assert, which trips
        # Bandit's B101 rule on the QGIS Plugins website's upload scanner).
        # No-op if a CI step already wrote this file first.
        src = Path(self.shared_dir) / "gitattributes"
        dst = Path(self.plugin_path) / ".gitattributes"
        QFile.copy(str(src), str(dst))

        # Render lifecycle test for iface-based plugin types
        is_processing = specification.template_map.get(
            "TemplateHasProcessingProvider", False
        )
        if not is_processing:
            self.populate_template(
                specification,
                self.shared_dir,
                "test_plugin_lifecycle.tmpl",
                "test/test_plugin_lifecycle.py",
            )

        # Render pyproject.toml at plugin root
        self.populate_template(
            specification, self.shared_dir, "pyproject.toml.tmpl", "pyproject.toml"
        )

        # Copy requirements-dev.txt to plugin root
        src = Path(self.shared_dir) / "requirements-dev.txt"
        dst = Path(self.plugin_path) / "requirements-dev.txt"
        QFile.copy(str(src), str(dst))

    def _prepare_i18n(self):
        """Copy the i18n folder."""
        scripts_source = Path(self.shared_dir) / "i18n"
        copy(str(scripts_source), str(Path(self.plugin_path) / "i18n"))

    def _write_qgis_plugin_ci_config(self, specification):
        """Write .qgis-plugin-ci, including whichever platform slugs are enabled."""
        lines = [
            "# qgis-plugin-ci configuration",
            "# See https://opengisch.github.io/qgis-plugin-ci/",
            f"plugin_path: {specification.module_name}",
        ]
        if specification.gen_qgis_plugin_ci:
            lines.append(f"github_organization_slug: {specification.github_org_slug}")
        if specification.gen_gitlab_ci:
            lines.append(f"gitlab_organization_slug: {specification.gitlab_namespace}")
        lines.append(f"project_slug: {specification.project_slug}")
        config_path = self.plugin_path / ".qgis-plugin-ci"
        with open(config_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    def _prepare_qgis_plugin_ci(self, specification):
        """Generate .qgis-plugin-ci config and GitHub Actions release workflow."""
        self._write_qgis_plugin_ci_config(specification)
        workflows_dir = self.plugin_path / ".github" / "workflows"
        workflows_dir.mkdir(exist_ok=True)
        QFile.copy(
            str(self.shared_dir / "github_release.yml"),
            str(workflows_dir / "release.yml"),
        )
        QFile.copy(
            str(self.shared_dir / "gitattributes"),
            str(self.plugin_path / ".gitattributes"),
        )

    def _prepare_gitlab_ci(self, specification):
        """Generate .qgis-plugin-ci config and GitLab CI release pipeline."""
        if not specification.gen_qgis_plugin_ci:
            # Only write the config if GitHub CI hasn't already written it
            self._write_qgis_plugin_ci_config(specification)
        QFile.copy(
            str(self.shared_dir / "gitlab_release.yml"),
            str(self.plugin_path / ".gitlab-ci.yml"),
        )
        QFile.copy(
            str(self.shared_dir / "gitattributes"),
            str(self.plugin_path / ".gitattributes"),
        )

    def _prepare_help(self):
        """Prepare the help directory."""
        # Create sphinx default project for help
        QDir().mkdir(str(self.plugin_path / "help"))
        QDir().mkdir(str(self.plugin_path / "help/build"))
        QDir().mkdir(str(self.plugin_path / "help/build/html"))
        QDir().mkdir(str(self.plugin_path / "help/source"))
        QDir().mkdir(str(self.plugin_path / "help/source/_static"))
        QDir().mkdir(str(self.plugin_path / "help/source/_templates"))
        # copy doc makefiles
        # noinspection PyCallByClass,PyTypeChecker
        QFile.copy(
            str(self.shared_dir / "help/make.py"),
            str(self.plugin_path / "help/make.py"),
        )
        # noinspection PyCallByClass,PyTypeChecker
        QFile.copy(
            str(self.shared_dir / "help/Makefile"),
            str(self.plugin_path / "help/Makefile"),
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
            t_file = QFile(self.template_dir / template_file)
            t_file.copy(self.plugin_path / output_name)

        QFile.copy(
            str(self.shared_dir / "LICENSE"),
            str(self.plugin_path / "LICENSE"),
        )

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
        content = Path(self.shared_dir / "readme.tmpl").read_text()
        template = Template(content)
        result_map = {
            **specification.template_map,
            "PluginDir": self.plugin_path,
            "TemplateModuleName": template_module_name,
            "UserPluginDir": self.user_plugin_dir,
        }
        popped = template.safe_substitute(result_map)
        # write the results info to the README txt file
        Path(self.plugin_path / "README.txt").write_text(popped, encoding="utf-8")

    def _prepare_metadata(self, specification):
        """Prepare metadata file.

        :param specification: Specification instance containing template
            replacement keys/values.
        :type specification: PluginSpecification
        """
        processing_provider = specification.template_map[
            "TemplateHasProcessingProvider"
        ]
        metadata_file = open(
            self.plugin_path / "metadata.txt", "w", encoding="utf-8"
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
            "# Since QGIS 3.8, a comma separated list of plugins to be installed\n"
        )
        metadata_file.write("# (or upgraded) can be specified.\n")
        metadata_file.write("# Check the documentation for more information.\n")
        metadata_file.write("# plugin_dependencies=\n\n")
        metadata_file.write(
            "# Category of the plugin: Raster, Vector, Database or Web\n"
        )
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
        template_file = open(
            self.shared_dir / "results.tmpl", encoding="utf-8"
        )
        content = Path(template_file.name).read_text()
        template = Template(content)
        ui_file = specification.template_map.get("TemplateUiFiles", "")
        what_next = (
            self.template.what_next_items_html(
                self.plugin_path, template_module_name, ui_file
            )
            if self.template is not None
            else ""
        )
        qpci_steps = ""
        if specification.gen_qgis_plugin_ci:
            qpci_steps += (
                "    <li>Initialize a git repository and push to GitHub: "
                "<code>git init &amp;&amp; git add . &amp;&amp; git commit -m"
                " 'initial commit' &amp;&amp; git push</code>\n"
                "    <li>Upload your first release manually using username/password"
                " (the token API requires the plugin to already exist on"
                " plugins.qgis.org)\n"
                "    <li>Add <b>QGIS_PLUGIN_TOKEN</b> as a repository secret"
                " (get it at plugins.qgis.org/plugins/"
                + template_module_name
                + "/tokens/create/): "
                "GitHub &rarr; Settings &rarr; Secrets and variables &rarr; Actions\n"
                "    <li>Create a GitHub Release to trigger the automated"
                " deployment workflow\n"
            )
        if specification.gen_gitlab_ci:
            qpci_steps += (
                "    <li>Initialize a git repository and push to GitLab: "
                "<code>git init &amp;&amp; git add . &amp;&amp; git commit -m"
                " 'initial commit' &amp;&amp; git push</code>\n"
                "    <li>Upload your first release manually using username/password"
                " (the token API requires the plugin to already exist on"
                " plugins.qgis.org)\n"
                "    <li>Add <b>QGIS_PLUGIN_TOKEN</b> as a CI/CD variable"
                " (get it at plugins.qgis.org/plugins/"
                + template_module_name
                + "/tokens/create/): "
                "GitLab &rarr; Settings &rarr; CI/CD &rarr; Variables\n"
                "    <li>Push a git tag to trigger the release pipeline\n"
            )
        result_map = {
            **specification.template_map,
            "PluginDir": self.plugin_path,
            "TemplateModuleName": template_module_name,
            "UserPluginDir": self.user_plugin_dir,
            "TemplateWhatNextItems": what_next,
            "TemplateQgisPluginCiSteps": qpci_steps,
        }
        results_popped = template.safe_substitute(result_map)
        # write the results info to the README HTML file

        Path(self.plugin_path / "README.html").write_text(results_popped)
        return results_popped, template_module_name

    def _create_plugin_directory(self):
        """Create the plugin directory using the module name."""
        raw_name = self.dialog.module_name.text().lower()
        module_name = "".join(c for c in raw_name if c.isalnum() or c == "_")
        self.plugin_path = self.plugin_path / module_name
        if not QDir().mkdir(str(self.plugin_path)):
            QMessageBox.critical(
                None,
                self.tr("Error"),
                self.tr(f"Could not create plugin directory:\n{self.plugin_path}"),
            )
            return False
        return True

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
        user_tag_list = Path.home() / ".plugin_tags.txt"
        if user_tag_list.exists():
            tag_file = user_tag_list
        else:
            tag_file = self.plugin_builder_path / "taglist.txt"

        with open(tag_file) as tf:
            tags = tf.readlines()

        model = QStandardItemModel()

        for tag in tags:
            item = QStandardItem(tag.rstrip("\n"))
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

    def run(self):
        """Run method that performs all the real work"""
        # create and show the dialog
        self.dialog = PluginBuilderDialog(stored_output_path=self._last_used_path())

        # get version
        cfg = configparser.ConfigParser()
        cfg.read(self.plugin_builder_path / "metadata.txt")
        version = cfg.get("general", "version")
        self.dialog.setWindowTitle(self.tr("QGIS Plugin Builder - {}").format(version))

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
        self.plugin_path = Path(self.dialog.output_directory.text())

        self._set_last_used_path(self.plugin_path)
        if not self._create_plugin_directory():
            return
        self.template = self.dialog.template()
        self.template_dir = self.template.subdir() / "template"
        self.shared_dir = self.plugin_builder_path / "plugin_templates" / "shared"

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

        if specification.gen_i18n:
            self._prepare_i18n()

        QFile.copy(
            str(self.shared_dir / "pre-commit-config.yaml"),
            str(self.plugin_path / ".pre-commit-config.yaml"),
        )

        if specification.gen_qgis_plugin_ci:
            self._prepare_qgis_plugin_ci(specification)

        if specification.gen_gitlab_ci:
            self._prepare_gitlab_ci(specification)

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
        template_file_path = template_dir / template_name
        output_name_path = self.plugin_path / output_name

        template_file = open(template_file_path, encoding="utf-8")
        content = template_file.read()
        template_file.close()
        template = Template(content)
        popped = template.safe_substitute(specification.template_map)
        plugin_file = open(output_name_path, "w", encoding="utf-8")
        plugin_file.write(popped)
        plugin_file.close()

    def show_help(self):
        """Display application help to the user."""
        help_file = self.plugin_builder_path / "help" / "index.html"
        if help_file.exists():
            QDesktopServices.openUrl(QUrl("file:///" + str(help_file)))
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
