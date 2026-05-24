# coding=utf-8
"""Tests for PluginBuilderDialog and PluginSpecification."""

from unittest.mock import patch

import pytest
from plugin_builder_dialog import PluginBuilderDialog
from plugin_specification import PluginSpecification


def _fill_dialog(dlg):
    """Populate a PluginBuilderDialog with valid test data."""
    dlg.class_name.setText("TestPlugin")
    dlg.title.setText("Test Plugin")
    dlg.description.setText("A test plugin")
    dlg.module_name.setText("test_plugin")
    dlg.plugin_version.setText("1.0.0")
    dlg.qgis_minimum_version.setText("4.0.0")
    dlg.qgis_maximum_version.setText("4.99")
    dlg.author.setText("Test Author")
    dlg.email_address.setText("test@example.com")
    dlg.about.setPlainText("This is a test plugin.")
    dlg.homepage.setText("https://github.com/testorg/test-plugin")
    dlg.tracker.setText("https://github.com/testorg/test-plugin/issues")
    dlg.repository.setText("https://github.com/testorg/test-plugin")
    dlg.tags.setText("test, qgis")


@pytest.fixture
def dialog(qgis_app):
    return PluginBuilderDialog()


# ---------------------------------------------------------------------------
# PluginSpecification
# ---------------------------------------------------------------------------


def test_specification_basic_fields(dialog):
    """PluginSpecification reads all basic dialog fields correctly."""
    _fill_dialog(dialog)
    spec = PluginSpecification(dialog)
    assert spec.class_name == "TestPlugin"
    assert spec.module_name == "test_plugin"
    assert spec.author == "Test Author"
    assert spec.email_address == "test@example.com"
    assert spec.gen_makefile is True
    assert spec.gen_pb_tool is True
    assert spec.gen_qgis_plugin_ci is False


def test_specification_qgis_plugin_ci_off(dialog):
    """When qgis_plugin_ci_cb is unchecked, CI fields are empty strings."""
    _fill_dialog(dialog)
    dialog.qgis_plugin_ci_cb.setChecked(False)
    spec = PluginSpecification(dialog)
    assert spec.gen_qgis_plugin_ci is False
    assert spec.github_org_slug == ""
    assert spec.project_slug == ""


def test_specification_qgis_plugin_ci_on(dialog):
    """When qgis_plugin_ci_cb is checked, CI fields are read into the spec."""
    _fill_dialog(dialog)
    dialog.qgis_plugin_ci_cb.setChecked(True)
    dialog.github_org_slug.setText("myorg")
    dialog.project_slug.setText("my-plugin")
    spec = PluginSpecification(dialog)
    assert spec.gen_qgis_plugin_ci is True
    assert spec.github_org_slug == "myorg"
    assert spec.project_slug == "my-plugin"
    assert spec.template_map["TemplateGitHubOrg"] == "myorg"
    assert spec.template_map["TemplateProjectSlug"] == "my-plugin"


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------


def test_next_page_skips_ci_when_unchecked(dialog):
    """_next_page_index skips page_ci (5) when neither CI option is selected."""
    dialog.qgis_plugin_ci_cb.setChecked(False)
    dialog.gitlab_ci_cb.setChecked(False)
    assert dialog._next_page_index(4) == 6


def test_next_page_includes_ci_when_checked(dialog):
    """_next_page_index goes to page_ci (5) when GitHub CI is selected."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    assert dialog._next_page_index(4) == 5


def test_next_page_includes_ci_when_gitlab_checked(dialog):
    """_next_page_index goes to page_ci (5) when GitLab CI is selected."""
    dialog.gitlab_ci_cb.setChecked(True)
    assert dialog._next_page_index(4) == 5


def test_next_page_sequential_elsewhere(dialog):
    """_next_page_index increments by 1 on all other pages."""
    for i in (0, 1, 2, 3, 5):
        assert dialog._next_page_index(i) == i + 1


def test_next_page_returns_none_at_last_page(dialog):
    """_next_page_index returns None on the last page to trigger accept()."""
    assert dialog._next_page_index(6) is None


def test_prev_page_skips_ci_when_unchecked(dialog):
    """_prev_page_index skips back over page_ci (5) when neither CI option is selected."""
    dialog.qgis_plugin_ci_cb.setChecked(False)
    dialog.gitlab_ci_cb.setChecked(False)
    assert dialog._prev_page_index(6) == 4


def test_prev_page_includes_ci_when_checked(dialog):
    """_prev_page_index goes to page_ci (5) when GitHub CI is selected."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    assert dialog._prev_page_index(6) == 5


def test_prev_page_includes_ci_when_gitlab_checked(dialog):
    """_prev_page_index goes to page_ci (5) when GitLab CI is selected."""
    dialog.gitlab_ci_cb.setChecked(True)
    assert dialog._prev_page_index(6) == 5


def test_prev_page_sequential_elsewhere(dialog):
    """_prev_page_index decrements by 1 on all other pages."""
    for i in (1, 2, 3, 4, 5):
        assert dialog._prev_page_index(i) == i - 1


# ---------------------------------------------------------------------------
# CI page validation
# ---------------------------------------------------------------------------


def test_validate_ci_page_empty_org(dialog):
    """validate_ci_page fails when GitHub CI is checked but org slug is empty."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    dialog.github_org_slug.setText("")
    dialog.project_slug.setText("my-plugin")
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_ci_page() is False


def test_validate_ci_page_empty_slug(dialog):
    """validate_ci_page fails when project slug is empty."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    dialog.github_org_slug.setText("myorg")
    dialog.project_slug.setText("")
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_ci_page() is False


def test_validate_ci_page_whitespace_only(dialog):
    """validate_ci_page fails when GitHub CI is checked and org is whitespace-only."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    dialog.github_org_slug.setText("   ")
    dialog.project_slug.setText("my-plugin")
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_ci_page() is False


def test_validate_ci_page_valid(dialog):
    """validate_ci_page passes when GitHub CI is checked and all fields are filled."""
    dialog.qgis_plugin_ci_cb.setChecked(True)
    dialog.github_org_slug.setText("myorg")
    dialog.project_slug.setText("my-plugin")
    assert dialog.validate_ci_page() is True


def test_validate_ci_page_gitlab_empty_namespace(dialog):
    """validate_ci_page fails when GitLab CI is checked but namespace is empty."""
    dialog.gitlab_ci_cb.setChecked(True)
    dialog.gitlab_namespace.setText("")
    dialog.project_slug.setText("my-plugin")
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_ci_page() is False


def test_validate_ci_page_gitlab_valid(dialog):
    """validate_ci_page passes when GitLab CI is checked and all fields are filled."""
    dialog.gitlab_ci_cb.setChecked(True)
    dialog.gitlab_namespace.setText("mygroup")
    dialog.project_slug.setText("my-plugin")
    assert dialog.validate_ci_page() is True


def test_specification_gitlab_ci_on(dialog):
    """When gitlab_ci_cb is checked, GitLab fields are read into the spec."""
    _fill_dialog(dialog)
    dialog.gitlab_ci_cb.setChecked(True)
    dialog.gitlab_namespace.setText("mygroup")
    dialog.project_slug.setText("my-plugin")
    spec = PluginSpecification(dialog)
    assert spec.gen_gitlab_ci is True
    assert spec.gitlab_namespace == "mygroup"
    assert spec.project_slug == "my-plugin"
    assert spec.template_map["TemplateGitLabNamespace"] == "mygroup"


# ---------------------------------------------------------------------------
# _populate_ci_fields
# ---------------------------------------------------------------------------


def test_populate_ci_fields_github_url(dialog):
    """GitHub URL is parsed to populate org slug and project slug."""
    dialog.repository.setText("https://github.com/myorg/my-plugin")
    dialog._populate_ci_fields()
    assert dialog.github_org_slug.text() == "myorg"
    assert dialog.project_slug.text() == "my-plugin"


def test_populate_ci_fields_github_url_with_git_suffix(dialog):
    """GitHub URL ending in .git is parsed correctly."""
    dialog.repository.setText("https://github.com/myorg/my-plugin.git")
    dialog._populate_ci_fields()
    assert dialog.github_org_slug.text() == "myorg"
    assert dialog.project_slug.text() == "my-plugin"


def test_populate_ci_fields_gitlab_url(dialog):
    """GitLab URL populates namespace and project slug, not GitHub org."""
    dialog.repository.setText("https://gitlab.com/mygroup/my-plugin")
    dialog._populate_ci_fields()
    assert dialog.github_org_slug.text() == ""
    assert dialog.gitlab_namespace.text() == "mygroup"
    assert dialog.project_slug.text() == "my-plugin"


def test_populate_ci_fields_non_matching_url(dialog):
    """Unrecognised host leaves all CI fields empty."""
    dialog.repository.setText("https://bitbucket.org/myorg/my-plugin")
    dialog._populate_ci_fields()
    assert dialog.github_org_slug.text() == ""
    assert dialog.gitlab_namespace.text() == ""
    assert dialog.project_slug.text() == ""


def test_populate_ci_fields_does_not_overwrite_existing(dialog):
    """_populate_ci_fields does not overwrite a field the user already filled."""
    dialog.repository.setText("https://github.com/myorg/my-plugin")
    dialog.github_org_slug.setText("existing-org")
    dialog._populate_ci_fields()
    assert dialog.github_org_slug.text() == "existing-org"
    assert dialog.project_slug.text() == "my-plugin"
