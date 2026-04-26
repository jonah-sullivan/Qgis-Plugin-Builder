__author__ = "timlinux"

# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**ISClipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""


__author__ = "tim@linfiniti.com"
__date__ = "20/01/2011"
__copyright__ = "Copyright 2012, Australia Indonesia Facility for " "Disaster Reduction"

import os
import unittest

from qgis.core import QgsProviderRegistry


from test.utilities import get_qgis_app
from .utilities import temp_dir, unique_filename
from plugin_builder import PluginBuilder, copy
from .qgis_interface import QgisInterface

QGIS_APP = get_qgis_app()


class FakePluginSpecification(object):
    """A fake of PluginSpecification for testing."""

    def __init__(self):
        """Constructor.

        After calling the constructor, the class properties
        self.template_map, self.experimental etc. will be set.

        """
        self.class_name = "FakePlugin"
        self.author = "Fake Author"
        self.description = "Fake Description"
        self.module_name = "fake_module"
        self.email_address = "fake@mail.com"
        self.menu_text = "Fake Menu"
        self.qgis_minimum_version = "3.0.0"
        self.qgis_maximum_version = "4.99"
        self.title = "A fake plugin"
        self.plugin_version = "1.0.0"
        self.homepage = "http://fakeqgisplugin.com"
        self.tracker = "http://github.com/timlinux/fakeplugin/issues"
        self.repository = "http://github.com/timlinux/fakeplugin/"
        self.about = "Fake about text"
        self.tags = "fake, qgis, plugin"
        # icon selection from disk will be added at a later version
        self.icon = "icon.png"
        self.experimental = False
        # Builder flags
        self.gen_i18n = True
        self.gen_help = True
        self.gen_tests = True
        self.gen_scripts = True
        self.gen_makefile = True
        self.gen_pb_tool = True
        # deprecated is always false for a new plugin
        self.deprecated = False
        self.build_year = 2001
        self.build_date = "31-01-2014"
        # Git will replace this with the sha - I do it a funny way below so
        # that this line below does not itself get substituted by git!
        self.vcs_format = "$Format:" + "%H$"

        self.template_map = {
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
            # Makefile
            "TemplatePyFiles": "%s_dialog.py" % self.module_name,
            "TemplateUiFiles": "%s_dialog_base.ui" % self.module_name,
            "TemplateExtraFiles": "icon.png",
            "TemplateQrcFiles": "resources.qrc",
            "TemplateRcFiles": "resources.py",
            # Menu
            "TemplateMenuText": self.menu_text,
            "TemplateMenuAddMethod": "addPluginToMenu",
            "TemplateMenuRemoveMethod": "removePluginMenu",
            "TemplateHasProcessingProvider": False,
        }


class QGISTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def test_qgis_environment(self):
        """QGIS environment has the expected providers"""

        registry = QgsProviderRegistry.instance()
        self.assertIn("gdal", registry.providerList())
        self.assertIn("ogr", registry.providerList())


class BuilderTest(unittest.TestCase):
    """Test the plugin builder."""

    def __init__(self, *args, **kwargs):
        super(BuilderTest, self).__init__(*args, **kwargs)
        # Define class members here....
        self.shared_dir = None
        self.template_dir = None
        self.specification = FakePluginSpecification()

    def setUp(self):
        """Setup run before each test."""
        self.shared_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "plugin_templates", "shared")
        )
        self.template_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "plugin_templates",
                "toolbutton_with_dialog",
                "template",
            )
        )

    def test_dir_copy(self):
        """Test that we can copy a directory of files.

        Path to copy to must not pre-exist so we create a parent dir
        and generate a temp dir name without actually creating it.
        """

        temp_path = temp_dir()
        temp_name = unique_filename(prefix="plugin_builder_")
        new_path = os.path.join(temp_path, temp_name)
        copy(os.path.join(self.shared_dir, "test"), new_path)
        test_file_path = os.path.join(new_path, "test_init.py")
        self.assertTrue(os.path.exists(test_file_path), test_file_path)

    def test_prepare_code(self):
        """Test the prepare code helper writes the expected output files."""
        temp_path = temp_dir()
        iface = QgisInterface(None)
        builder = PluginBuilder(iface)
        builder.shared_dir = self.shared_dir
        builder.template_dir = self.template_dir
        builder.plugin_path = temp_path
        builder._prepare_code(self.specification)
        for expected in ["Makefile", "pb_tool.cfg", "__init__.py", "fake_module.py"]:
            self.assertTrue(
                os.path.exists(os.path.join(temp_path, expected)),
                "%s was not created" % expected,
            )

    def test_prepare_results_html(self):
        """Test the prepare results helper works."""
        temp_path = temp_dir()
        iface = QgisInterface(None)
        builder = PluginBuilder(iface)
        builder.shared_dir = self.shared_dir
        builder.template_dir = self.template_dir
        builder.plugin_path = temp_path
        results_popped, template_module_name = builder._prepare_results_html(
            self.specification
        )
        self.assertIn("You just built a plugin for QGIS!", results_popped)
        self.assertEqual(template_module_name, "fake_module")

    def test_prepare_readme(self):
        """Test that README.txt is written with the substituted plugin names."""
        temp_path = temp_dir()
        iface = QgisInterface(None)
        builder = PluginBuilder(iface)
        builder.shared_dir = self.shared_dir
        builder.template_dir = self.template_dir
        builder.plugin_path = temp_path
        builder._prepare_readme(self.specification, "fake_module")
        readme_path = os.path.join(temp_path, "README.txt")
        self.assertTrue(os.path.exists(readme_path))
        content = open(readme_path).read()
        self.assertIn("FakePlugin", content)
        self.assertIn("fake_module", content)

    def test_prepare_metadata(self):
        """Test that metadata.txt is written with the expected required fields."""
        temp_path = temp_dir()
        iface = QgisInterface(None)
        builder = PluginBuilder(iface)
        builder.shared_dir = self.shared_dir
        builder.template_dir = self.template_dir
        builder.plugin_path = temp_path

        class FakeTemplate:
            category = "Raster"

        builder.template = FakeTemplate()

        builder._prepare_metadata(self.specification)
        metadata_path = os.path.join(temp_path, "metadata.txt")
        self.assertTrue(os.path.exists(metadata_path))
        content = open(metadata_path).read()
        self.assertIn("name=A fake plugin", content)
        self.assertIn("author=Fake Author", content)
        self.assertIn("email=fake@mail.com", content)
        self.assertIn("qgisMinimumVersion=3.0.0", content)
        self.assertIn("qgisMaximumVersion=4.99", content)
        self.assertIn("[general]", content)
