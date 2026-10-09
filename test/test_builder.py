# coding=utf-8
"""Tests for the plugin builder."""

import platform
from pathlib import Path

import pytest
from plugin_builder import PluginBuilder, copy
from qgis.core import QgsProviderRegistry
from qgis_dirs import _qgis_dir_location, deployment_dir


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
        self.gen_makefile = True
        self.gen_pb_tool = True
        self.gen_qgis_plugin_ci = False
        self.gen_gitlab_ci = False
        self.github_org_slug = ""
        self.gitlab_namespace = ""
        self.project_slug = ""
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
            "TemplatePyFiles": f"{self.module_name}_dialog.py",
            "TemplateUiFiles": f"{self.module_name}_dialog_base.ui",
            "TemplateExtraFiles": "icon.png",
            "TemplateQrcFiles": "resources.qrc",
            "TemplateRcFiles": "resources.py",
            "TemplateMenuText": self.menu_text,
            "TemplateMenuAddMethod": "addPluginToMenu",
            "TemplateMenuRemoveMethod": "removePluginMenu",
            "TemplateHasProcessingProvider": False,
            "TemplateGitHubOrg": "",
            "TemplateGitLabNamespace": "",
            "TemplateProjectSlug": "",
            "TemplateQgisPluginCiSteps": "",
        }


@pytest.fixture
def spec():
    return FakePluginSpecification()


@pytest.fixture
def builder(qgis_app, qgis_iface, tmp_path):
    _templates = Path(__file__).parent.parent / "pluginbuilder4" / "plugin_templates"
    b = PluginBuilder(qgis_iface)
    b.shared_dir = _templates / "shared"
    b.template_dir = _templates / "toolbutton_with_dialog" / "template"
    b.plugin_path = tmp_path
    return b


def test_qgis_environment(qgis_app):
    """QGIS environment has the expected providers."""
    r = QgsProviderRegistry.instance()
    assert "gdal" in r.providerList()
    assert "ogr" in r.providerList()


def test_dir_copy(builder, tmp_path):
    """Copying a template sub-directory produces the expected files."""
    dest = tmp_path / "plugin_builder_test"
    copy(Path(builder.shared_dir) / "test", dest)
    assert (dest / "test_init.py.tmpl").exists()


def test_prepare_code(builder, spec):
    """_prepare_code writes the expected output files."""
    builder._prepare_code(spec)
    for expected in ["Makefile", "pb_tool.cfg", "__init__.py", "fake_module.py"]:
        assert (Path(builder.plugin_path) / Path(expected)).exists(), (
            f"{expected} was not created"
        )


def test_prepare_results_html(builder, spec):
    """_prepare_results_html returns the expected content and module name."""
    results_popped, template_module_name = builder._prepare_results_html(spec)
    assert "You just built a plugin for QGIS!" in results_popped
    assert template_module_name == "fake_module"


def test_prepare_readme(builder, spec):
    """_prepare_readme writes README.txt with substituted plugin names."""
    builder._prepare_readme(spec, "fake_module")
    readme_path = Path(builder.plugin_path) / "README.txt"
    assert readme_path.exists()
    content = Path(readme_path).read_text()
    assert "FakePlugin" in content
    assert "fake_module" in content


def test_prepare_metadata(builder, spec):
    """_prepare_metadata writes metadata.txt with required fields."""

    class FakeTemplate:
        category = "Raster"

    builder.template = FakeTemplate()
    builder._prepare_metadata(spec)
    metadata_path = Path(builder.plugin_path) / "metadata.txt"
    assert metadata_path.exists()
    content = Path(metadata_path).read_text()
    assert "name=A fake plugin" in content
    assert "author=Fake Author" in content
    assert "email=fake@mail.com" in content
    assert "qgisMinimumVersion=4.0.0" in content
    assert "qgisMaximumVersion=4.99" in content
    assert "[general]" in content


def test_deployment_dir():
    """deployment_dir points to the QGIS4 plugins directory for the current OS."""
    expected_suffix = _qgis_dir_location[platform.system()]
    assert deployment_dir == Path.home() / expected_suffix
    assert "QGIS4" in str(deployment_dir)
    assert deployment_dir.is_absolute()


def test_copy_single_file(tmp_path):
    """copy() falls back to shutil.copy when source is a file not a directory."""
    src = tmp_path / "source.txt"
    src.write_text("hello")
    dest = str(tmp_path / "dest.txt")
    copy(str(src), dest)
    assert Path(dest).exists()
    assert Path(dest).read_text() == "hello"


def test_prepare_i18n(builder):
    """_prepare_i18n copies the i18n directory into plugin_path."""
    builder._prepare_i18n()
    assert (Path(builder.plugin_path) / "i18n").is_dir()


def test_prepare_tests(builder, spec):
    """_prepare_tests copies test files and renders lifecycle and pyproject
    templates."""
    builder._prepare_tests(spec)
    assert (Path(builder.plugin_path) / "test").is_dir()
    assert (Path(builder.plugin_path) / "test" / "test_plugin_lifecycle.py").exists()
    assert (Path(builder.plugin_path) / "pyproject.toml").exists()
    gitattributes_path = Path(builder.plugin_path) / ".gitattributes"
    assert gitattributes_path.exists()
    with open(gitattributes_path) as f:
        assert "test/ export-ignore" in f.read()


def test_prepare_help(builder):
    """_prepare_help creates the expected help directory structure."""
    builder._prepare_help()
    for subdir in [
        "help",
        Path("help") / "build",
        Path("help") / "build" / "html",
        Path("help") / "source",
        Path("help") / "source" / "_static",
        Path("help") / "source" / "_templates",
    ]:
        assert (builder.plugin_path / subdir).is_dir()
        assert (builder.plugin_path / "help" / "make.py").is_file()
        assert (builder.plugin_path / "help" / "Makefile").is_file()


def test_prepare_qgis_plugin_ci(builder, spec):
    """_prepare_qgis_plugin_ci writes
    .qgis-plugin-ci, .github/workflows/qgis-plugin-ci.yml,
    release.yml, and .gitattributes."""
    spec.gen_qgis_plugin_ci = True
    spec.github_org_slug = "myorg"
    spec.project_slug = "my-plugin"
    builder._prepare_qgis_plugin_ci(spec)
    assert (builder.plugin_path / ".qgis-plugin-ci").exists()
    assert (builder.plugin_path / ".github" / "workflows" / "release.yml").exists()
    assert (builder.plugin_path / ".gitattributes").exists()
    content = (builder.plugin_path / ".qgis-plugin-ci").read_text()
    assert "myorg" in content
    assert "my-plugin" in content
    assert "fake_module" in content


def test_prepare_results_html_with_qgis_plugin_ci(builder, spec):
    """_prepare_results_html includes CI/CD steps when gen_qgis_plugin_ci is True."""
    spec.gen_qgis_plugin_ci = True
    results_popped, _ = builder._prepare_results_html(spec)
    assert "QGIS_PLUGIN_TOKEN" in results_popped
    assert "GitHub Release" in results_popped


def test_prepare_gitlab_ci(builder, spec):
    """_prepare_gitlab_ci writes .gitlab-ci.yml, .qgis-plugin-ci, and .gitattributes."""
    spec.gen_gitlab_ci = True
    spec.gitlab_namespace = "mygroup"
    spec.project_slug = "my-plugin"
    builder._prepare_gitlab_ci(spec)
    assert (builder.plugin_path / ".gitlab-ci.yml").exists()
    assert (builder.plugin_path / ".qgis-plugin-ci").exists()
    assert (builder.plugin_path / ".gitattributes").exists()
    content = (builder.plugin_path / ".qgis-plugin-ci").read_text()
    assert "mygroup" in content
    assert "my-plugin" in content
    assert "fake_module" in content


def test_write_qgis_plugin_ci_config_both_platforms(builder, spec):
    """Config includes both slugs when both GitHub and GitLab CI are enabled."""
    spec.gen_qgis_plugin_ci = True
    spec.github_org_slug = "ghorg"
    spec.gen_gitlab_ci = True
    spec.gitlab_namespace = "glgroup"
    spec.project_slug = "my-plugin"
    builder._write_qgis_plugin_ci_config(spec)
    content = (builder.plugin_path / ".qgis-plugin-ci").read_text()
    assert "github_organization_slug: ghorg" in content
    assert "gitlab_organization_slug: glgroup" in content
    assert "project_slug: my-plugin" in content


def test_prepare_results_html_with_gitlab_ci(builder, spec):
    """_prepare_results_html includes GitLab steps when gen_gitlab_ci is True."""
    spec.gen_gitlab_ci = True
    spec.gitlab_namespace = "mygroup"
    spec.project_slug = "my-plugin"
    results_popped, _ = builder._prepare_results_html(spec)
    assert "QGIS_PLUGIN_TOKEN" in results_popped
    assert (
        "git tag" in results_popped.lower()
        or "CI_COMMIT_TAG" in results_popped
        or "GitLab" in results_popped
    )


def test_prepare_specific_files(builder, spec):
    """_prepare_specific_files renders
    template files and copies static files."""

    class FakeTemplate:
        def template_files(self, specification):
            return {
                "module_name_dialog.tmpl": (f"{specification.module_name}_dialog.py"),
                "module_name_dialog_base.ui.tmpl": (
                    f"{specification.module_name}_dialog_base.ui"
                ),
            }

        def copy_files(self, specification):
            return {"icon.png": "icon.png"}

    builder.template = FakeTemplate()
    builder._prepare_specific_files(spec)
    assert (builder.plugin_path / "fake_module_dialog.py").exists()
    assert (builder.plugin_path / "fake_module_dialog_base.ui").exists()
    assert (builder.plugin_path / "icon.png").exists()
