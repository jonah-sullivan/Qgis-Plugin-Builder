# coding=utf-8
"""Tests for the plugin builder."""

import os
import platform

import pytest
from qgis.core import QgsProviderRegistry

from plugin_builder import PluginBuilder, copy
from qgis_dirs import _qgis_dir_location, deployment_dir
from test.utilities import unique_filename


class FakePluginSpecification:
    """A fake of PluginSpecification for testing."""

    def __init__(self):
        self.class_name = "FakePlugin"
        self.author = "Fake Author"
        self.description = "Fake Description"
        self.module_name = "fake_module"
        self.email_address = "fake@mail.com"
        self.menu_text = "Fake Menu"
        self.qgis_minimum_version = "4.0.0"
        self.qgis_maximum_version = "4.99"
        self.title = "A fake plugin"
        self.plugin_version = "1.0.0"
        self.homepage = "http://fakeqgisplugin.com"
        self.tracker = "http://github.com/timlinux/fakeplugin/issues"
        self.repository = "http://github.com/timlinux/fakeplugin/"
        self.about = "Fake about text"
        self.tags = "fake, qgis, plugin"
        self.icon = "icon.png"
        self.experimental = False
        self.gen_i18n = True
        self.gen_help = True
        self.gen_tests = True
        self.gen_scripts = True
        self.gen_makefile = True
        self.gen_pb_tool = True
        self.deprecated = False
        self.build_year = 2001
        self.build_date = "31-01-2014"
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
            "TemplatePyFiles": "%s_dialog.py" % self.module_name,
            "TemplateUiFiles": "%s_dialog_base.ui" % self.module_name,
            "TemplateExtraFiles": "icon.png",
            "TemplateQrcFiles": "resources.qrc",
            "TemplateRcFiles": "resources.py",
            "TemplateMenuText": self.menu_text,
            "TemplateMenuAddMethod": "addPluginToMenu",
            "TemplateMenuRemoveMethod": "removePluginMenu",
            "TemplateHasProcessingProvider": False,
        }


@pytest.fixture
def spec():
    return FakePluginSpecification()


@pytest.fixture
def builder(qgis_app, qgis_iface, tmp_path):
    b = PluginBuilder(qgis_iface)
    b.shared_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "plugin_templates", "shared"
        )
    )
    b.template_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "plugin_templates",
            "toolbutton_with_dialog",
            "template",
        )
    )
    b.plugin_path = str(tmp_path)
    return b


def test_qgis_environment(qgis_app):
    """QGIS environment has the expected providers."""
    r = QgsProviderRegistry.instance()
    assert "gdal" in r.providerList()
    assert "ogr" in r.providerList()


def test_dir_copy(builder):
    """Copying a template sub-directory produces the expected files."""
    dest = unique_filename(prefix="plugin_builder_")
    copy(os.path.join(builder.shared_dir, "test"), dest)
    assert os.path.exists(os.path.join(dest, "test_init.py"))


def test_prepare_code(builder, spec):
    """_prepare_code writes the expected output files."""
    builder._prepare_code(spec)
    for expected in ["Makefile", "pb_tool.cfg", "__init__.py", "fake_module.py"]:
        assert os.path.exists(
            os.path.join(builder.plugin_path, expected)
        ), f"{expected} was not created"


def test_prepare_results_html(builder, spec):
    """_prepare_results_html returns the expected content and module name."""
    results_popped, template_module_name = builder._prepare_results_html(spec)
    assert "You just built a plugin for QGIS!" in results_popped
    assert template_module_name == "fake_module"


def test_prepare_readme(builder, spec):
    """_prepare_readme writes README.txt with substituted plugin names."""
    builder._prepare_readme(spec, "fake_module")
    readme_path = os.path.join(builder.plugin_path, "README.txt")
    assert os.path.exists(readme_path)
    with open(readme_path) as f:
        content = f.read()
    assert "FakePlugin" in content
    assert "fake_module" in content


def test_prepare_metadata(builder, spec):
    """_prepare_metadata writes metadata.txt with required fields."""

    class FakeTemplate:
        category = "Raster"

    builder.template = FakeTemplate()
    builder._prepare_metadata(spec)
    metadata_path = os.path.join(builder.plugin_path, "metadata.txt")
    assert os.path.exists(metadata_path)
    with open(metadata_path) as f:
        content = f.read()
    assert "name=A fake plugin" in content
    assert "author=Fake Author" in content
    assert "email=fake@mail.com" in content
    assert "qgisMinimumVersion=4.0.0" in content
    assert "qgisMaximumVersion=4.99" in content
    assert "[general]" in content


def test_deployment_dir():
    """deployment_dir points to the QGIS4 plugins directory for the current OS."""
    expected_suffix = _qgis_dir_location[platform.system()]
    assert deployment_dir.endswith(expected_suffix)
    assert "QGIS4" in deployment_dir
    assert os.path.isabs(deployment_dir)


def test_copy_single_file(tmp_path):
    """copy() falls back to shutil.copy when source is a file not a directory."""
    src = tmp_path / "source.txt"
    src.write_text("hello")
    dest = str(tmp_path / "dest.txt")
    copy(str(src), dest)
    assert os.path.exists(dest)
    with open(dest) as f:
        assert f.read() == "hello"


def test_prepare_scripts(builder):
    """_prepare_scripts copies the scripts directory into plugin_path."""
    builder._prepare_scripts()
    assert os.path.isdir(os.path.join(builder.plugin_path, "scripts"))


def test_prepare_i18n(builder):
    """_prepare_i18n copies the i18n directory into plugin_path."""
    builder._prepare_i18n()
    assert os.path.isdir(os.path.join(builder.plugin_path, "i18n"))


def test_prepare_tests(builder, spec):
    """_prepare_tests copies test files and renders lifecycle and pyproject templates."""
    builder._prepare_tests(spec)
    assert os.path.isdir(os.path.join(builder.plugin_path, "test"))
    assert os.path.exists(
        os.path.join(builder.plugin_path, "test", "test_plugin_lifecycle.py")
    )
    assert os.path.exists(os.path.join(builder.plugin_path, "pyproject.toml"))


def test_prepare_help(builder):
    """_prepare_help creates the expected help directory structure."""
    builder._prepare_help()
    for subdir in [
        "help",
        os.path.join("help", "build"),
        os.path.join("help", "build", "html"),
        os.path.join("help", "source"),
        os.path.join("help", "source", "_static"),
        os.path.join("help", "source", "_templates"),
    ]:
        assert os.path.isdir(os.path.join(builder.plugin_path, subdir))


def test_prepare_specific_files(builder, spec):
    """_prepare_specific_files renders template files and copies static files."""

    class FakeTemplate:
        def template_files(self, specification):
            return {
                "module_name_dialog.tmpl": (
                    "%s_dialog.py" % specification.module_name
                ),
                "module_name_dialog_base.ui.tmpl": (
                    "%s_dialog_base.ui" % specification.module_name
                ),
            }

        def copy_files(self, specification):
            return {"icon.png": "icon.png"}

    builder.template = FakeTemplate()
    builder._prepare_specific_files(spec)
    assert os.path.exists(
        os.path.join(builder.plugin_path, "fake_module_dialog.py")
    )
    assert os.path.exists(
        os.path.join(builder.plugin_path, "fake_module_dialog_base.ui")
    )
    assert os.path.exists(os.path.join(builder.plugin_path, "icon.png"))
