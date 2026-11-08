# coding=utf-8
"""Tests for PluginBuilderDialog and PluginSpecification."""

from unittest.mock import patch

import pytest
from plugin_builder_dialog import PluginBuilderDialog
from plugin_specification import PluginSpecification


@pytest.fixture
def dialog(qgis_app):
    return PluginBuilderDialog()


# ---------------------------------------------------------------------------
# PluginSpecification
# ---------------------------------------------------------------------------


def test_specification_basic_fields(dialog, fill_dialog):
    """PluginSpecification reads all basic dialog fields correctly."""
    fill_dialog(dialog)
    spec = PluginSpecification(dialog)
    assert spec.class_name == "TestPlugin"
    assert spec.module_name == "test_plugin"
    assert spec.author == "Test Author"
    assert spec.email_address == "test@example.com"
    assert spec.gen_makefile is True
    assert spec.gen_pb_tool is True
    assert spec.gen_qgis_plugin_ci is False


def test_specification_qgis_plugin_ci_off(dialog, fill_dialog):
    """When qgis_plugin_ci_cb is unchecked, CI fields are empty strings."""
    fill_dialog(dialog)
    dialog.qgis_plugin_ci_cb.setChecked(False)
    spec = PluginSpecification(dialog)
    assert spec.gen_qgis_plugin_ci is False
    assert spec.github_org_slug == ""
    assert spec.project_slug == ""


def test_specification_qgis_plugin_ci_on(dialog, fill_dialog):
    """When qgis_plugin_ci_cb is checked, CI fields are read into the spec."""
    fill_dialog(dialog)
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
    """_prev_page_index skips back over page_ci (5)
    when neither CI option is selected."""
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


def test_specification_gitlab_ci_on(dialog, fill_dialog):
    """When gitlab_ci_cb is checked, GitLab fields are read into the spec."""
    fill_dialog(dialog)
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


# ---------------------------------------------------------------------------
# Field validation
# ---------------------------------------------------------------------------


def test_validate_entries_valid(dialog, fill_dialog):
    """validate_entries passes and shows no warning for a complete form."""
    fill_dialog(dialog)
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_entries() is True
    warn.assert_not_called()


@pytest.mark.parametrize(
    "field, value",
    [
        ("class_name", ""),
        ("title", ""),
        ("description", ""),
        ("module_name", ""),
        ("author", ""),
        ("email_address", ""),
        ("plugin_version", "1.x"),
        ("plugin_version", "1"),
        ("qgis_minimum_version", "four"),
        ("qgis_maximum_version", "4.beta"),
        ("qgis_maximum_version", "4.0.0"),  # equal to minimum
        ("qgis_maximum_version", "3.40"),  # below minimum
    ],
)
def test_validate_entries_invalid(dialog, fill_dialog, field, value):
    """validate_entries fails and warns for a missing or bad field."""
    fill_dialog(dialog)
    getattr(dialog, field).setText(value)
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_entries() is False
    warn.assert_called_once()


def test_validate_entries_max_version_required(dialog, fill_dialog):
    """The maximum QGIS version is a required field."""
    fill_dialog(dialog)
    dialog.qgis_maximum_version.setText("")
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_entries() is False
    assert "required fields are missing" in warn.call_args.args[2]


@pytest.mark.parametrize(
    "field, value, expected",
    [
        ("class_name", "my test plugin", "MyTestPlugin"),
        ("class_name", "Plügin", "Plgin"),
        ("module_name", "My-Plugin!", "myplugin"),
    ],
)
def test_validate_entries_fixes_names(dialog, fill_dialog, field, value, expected):
    """Bad class/module names are corrected in place, but the user is
    still stopped so they can see the change."""
    fill_dialog(dialog)
    getattr(dialog, field).setText(value)
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_entries() is False
    assert getattr(dialog, field).text() == expected
    # A second pass with the corrected name succeeds
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_entries() is True


def test_validate_about(dialog):
    """validate_about requires non-empty about text."""
    dialog.about.setPlainText("")  # .ui pre-fills a placeholder
    with patch("plugin_builder_dialog.QMessageBox.warning"):
        assert dialog.validate_about() is False
    dialog.about.setPlainText("Does things.")
    assert dialog.validate_about() is True


@pytest.mark.parametrize(
    "tracker, repository, ok",
    [
        ("https://github.com/o/p/issues", "https://github.com/o/p", True),
        ("http://example.com/issues", "http://example.com/repo", True),
        ("", "https://github.com/o/p", False),
        ("https://github.com/o/p/issues", "", False),
        ("github.com/o/p/issues", "https://github.com/o/p", False),
        ("https://github.com/o/p/issues", "git@github.com:o/p.git", False),
    ],
)
def test_validate_publication(dialog, tracker, repository, ok):
    """Tracker and repository are required and must be http(s) URLs."""
    dialog.tracker.setText(tracker)
    dialog.repository.setText(repository)
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_publication() is ok
    assert warn.called is not ok


def test_validate_output_directory_empty(dialog):
    dialog.output_directory.setText("")
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_output_directory() is False
    assert "select an output directory" in warn.call_args.args[2]


def test_validate_output_directory_missing(dialog, tmp_path):
    dialog.output_directory.setText(str(tmp_path / "does_not_exist"))
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_output_directory() is False
    assert "does not exist" in warn.call_args.args[2]


def test_validate_output_directory_plugin_folder_exists(dialog, tmp_path):
    """Generating into an existing plugin folder is refused, not overwritten."""
    dialog.module_name.setText("test_plugin")
    (tmp_path / "test_plugin").mkdir()
    dialog.output_directory.setText(str(tmp_path))
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_output_directory() is False
    assert "already exists" in warn.call_args.args[2]


def test_show_output_info_existing_folder(dialog, tmp_path):
    """The final page warns, in red, that an existing folder blocks Generate."""
    dialog.show_output_info(tmp_path)
    text = dialog.lbl_full_output_path.text()
    assert "already exists" in text
    assert "overwrite" not in text
    assert "red" in dialog.lbl_full_output_path.styleSheet()


def test_show_output_info_new_folder_clears_warning(dialog, tmp_path):
    """Picking a free folder after an existing one removes the warning."""
    dialog.show_output_info(tmp_path)
    dialog.show_output_info(tmp_path / "new_plugin")
    assert dialog.lbl_full_output_path.text() == str(tmp_path / "new_plugin")
    assert "red" not in dialog.lbl_full_output_path.styleSheet()


def test_validate_output_directory_valid(dialog, tmp_path):
    dialog.module_name.setText("test_plugin")
    dialog.output_directory.setText(str(tmp_path))
    with patch("plugin_builder_dialog.QMessageBox.warning") as warn:
        assert dialog.validate_output_directory() is True
    warn.assert_not_called()
