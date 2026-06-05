# coding=utf-8
"""Tests for the three plugin template classes and the base PluginTemplate."""

import os

import pytest
from plugin_builder_dialog import PluginBuilderDialog
from plugin_templates import templates
from plugin_templates.plugin_template import PluginTemplate

# Obtain concrete template instances via the factory so that the nested
# relative imports (from ...qgis_dirs import deployment_dir) resolve
# correctly inside the _pluginbuilder synthetic package.
_templates = templates()
ToolbuttonWithDialogPluginTemplate = type(_templates[0])
ToolbuttonWithDockWidgetPluginTemplate = type(_templates[1])
ProcessingProviderPluginTemplate = type(_templates[2])


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


class FakeSpec:
    module_name = "my_plugin"
    gen_tests = False


class FakeSpecWithTests:
    module_name = "my_plugin"
    gen_tests = True


@pytest.fixture
def dialog(qgis_app):
    return PluginBuilderDialog()


def _select_template(dialog, index):
    """Switch the wizard to template *index* and return the loaded subframe."""
    dialog.template_cbox.setCurrentIndex(index)
    return dialog.template_subframe


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------


def test_base_descr_raises():
    t = PluginTemplate()
    with pytest.raises(NotImplementedError):
        t.descr()


def test_base_subdir_raises():
    t = PluginTemplate()
    with pytest.raises(NotImplementedError):
        t.subdir()


def test_base_template_map_returns_empty():
    assert PluginTemplate().template_map(None, None) == {}


def test_base_template_files_returns_empty():
    assert PluginTemplate().template_files(None) == {}


def test_base_copy_files_returns_empty():
    assert PluginTemplate().copy_files(None) == {}


def test_base_what_next_items_html():
    html = PluginTemplate().what_next_items_html(
        "/tmp/plugin", "my_plugin", "my_plugin_dialog_base.ui"
    )
    assert "my_plugin.py" in html
    assert "my_plugin_dialog_base.ui" in html
    assert "icon.png" in html


# ---------------------------------------------------------------------------
# templates() factory
# ---------------------------------------------------------------------------


def test_templates_returns_three():
    assert len(templates()) == 3


def test_templates_descriptions():
    descs = [t.descr() for t in templates()]
    assert "Tool button with dialog" in descs
    assert "Tool button with dock widget" in descs
    assert "Processing Provider" in descs


# ---------------------------------------------------------------------------
# ToolbuttonWithDialogPluginTemplate
# ---------------------------------------------------------------------------


def test_dialog_template_descr():
    assert ToolbuttonWithDialogPluginTemplate().descr() == "Tool button with dialog"


def test_dialog_template_subdir_exists():
    path = ToolbuttonWithDialogPluginTemplate().subdir()
    assert os.path.isdir(path)


def test_dialog_template_copy_files():
    assert ToolbuttonWithDialogPluginTemplate().copy_files(FakeSpec()) == {
        "icon.png": "icon.png"
    }


def test_dialog_template_files_without_tests():
    files = ToolbuttonWithDialogPluginTemplate().template_files(FakeSpec())
    assert "my_plugin_dialog.py" in files.values()
    assert "my_plugin_dialog_base.ui" in files.values()
    assert not any("test_" in v for v in files.values())


def test_dialog_template_files_with_tests():
    files = ToolbuttonWithDialogPluginTemplate().template_files(FakeSpecWithTests())
    assert any("test_my_plugin_dialog.py" in v for v in files.values())
    assert any("test_resources.py" in v for v in files.values())


def test_dialog_template_map_plugins_menu(dialog):
    subframe = _select_template(dialog, 0)
    subframe.menu_text.setText("Run Tool")
    subframe.menu_location.setCurrentText("Plugins")
    result = ToolbuttonWithDialogPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateMenuText"] == "Run Tool"
    assert result["TemplateMenuAddMethod"] == "addPluginToMenu"
    assert result["TemplateMenuRemoveMethod"] == "removePluginMenu"
    assert result["TemplateHasProcessingProvider"] is False


def test_dialog_template_map_vector_menu(dialog):
    subframe = _select_template(dialog, 0)
    subframe.menu_text.setText("Run Tool")
    subframe.menu_location.setCurrentText("Vector")
    result = ToolbuttonWithDialogPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateMenuAddMethod"] == "addPluginToVectorMenu"
    assert result["TemplateMenuRemoveMethod"] == "removePluginVectorMenu"


def test_dialog_template_map_ui_file(dialog):
    _select_template(dialog, 0)
    result = ToolbuttonWithDialogPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateUiFiles"] == "my_plugin_dialog_base.ui"
    assert result["TemplatePyFiles"] == "my_plugin_dialog.py"


# ---------------------------------------------------------------------------
# ToolbuttonWithDockWidgetPluginTemplate
# ---------------------------------------------------------------------------


def test_dockwidget_template_descr():
    assert (
        ToolbuttonWithDockWidgetPluginTemplate().descr()
        == "Tool button with dock widget"
    )


def test_dockwidget_template_subdir_exists():
    assert os.path.isdir(ToolbuttonWithDockWidgetPluginTemplate().subdir())


def test_dockwidget_template_copy_files():
    assert ToolbuttonWithDockWidgetPluginTemplate().copy_files(FakeSpec()) == {
        "icon.png": "icon.png"
    }


def test_dockwidget_template_files_without_tests():
    files = ToolbuttonWithDockWidgetPluginTemplate().template_files(FakeSpec())
    assert "my_plugin_dockwidget.py" in files.values()
    assert "my_plugin_dockwidget_base.ui" in files.values()
    assert not any("test_" in v for v in files.values())


def test_dockwidget_template_files_with_tests():
    files = ToolbuttonWithDockWidgetPluginTemplate().template_files(FakeSpecWithTests())
    assert any("test_my_plugin_dockwidget.py" in v for v in files.values())
    assert any("test_resources.py" in v for v in files.values())


def test_dockwidget_template_map_left_dock(dialog):
    subframe = _select_template(dialog, 1)
    subframe.menu_text.setText("Show Panel")
    subframe.menu_location.setCurrentText("Plugins")
    subframe.dockwidget_area.setCurrentText("Left")
    dialog.tabify_dockwidget.setChecked(False)
    result = ToolbuttonWithDockWidgetPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateMenuText"] == "Show Panel"
    assert "LeftDockWidgetArea" in result["TemplateAddDockWidgetCall"]
    assert "addDockWidget" in result["TemplateAddDockWidgetCall"]
    assert result["TemplateHasProcessingProvider"] is False


def test_dockwidget_template_map_tabified(dialog):
    subframe = _select_template(dialog, 1)
    subframe.menu_text.setText("Show Panel")
    subframe.menu_location.setCurrentText("Plugins")
    subframe.dockwidget_area.setCurrentText("Right")
    dialog.tabify_dockwidget.setChecked(True)
    result = ToolbuttonWithDockWidgetPluginTemplate().template_map(FakeSpec(), dialog)
    assert "addTabifiedDockWidget" in result["TemplateAddDockWidgetCall"]
    assert "RightDockWidgetArea" in result["TemplateAddDockWidgetCall"]


def test_dockwidget_template_map_non_plugins_menu(dialog):
    subframe = _select_template(dialog, 1)
    subframe.menu_text.setText("Show Panel")
    subframe.menu_location.setCurrentText("Raster")
    subframe.dockwidget_area.setCurrentText("Top")
    dialog.tabify_dockwidget.setChecked(False)
    result = ToolbuttonWithDockWidgetPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateMenuAddMethod"] == "addPluginToRasterMenu"
    assert result["TemplateMenuRemoveMethod"] == "removePluginRasterMenu"


def test_dockwidget_template_map_ui_file(dialog):
    _select_template(dialog, 1)
    result = ToolbuttonWithDockWidgetPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateUiFiles"] == "my_plugin_dockwidget_base.ui"
    assert result["TemplatePyFiles"] == "my_plugin_dockwidget.py"


# ---------------------------------------------------------------------------
# ProcessingProviderPluginTemplate
# ---------------------------------------------------------------------------


def test_processing_template_descr():
    assert ProcessingProviderPluginTemplate().descr() == "Processing Provider"


def test_processing_template_subdir_exists():
    assert os.path.isdir(ProcessingProviderPluginTemplate().subdir())


def test_processing_template_files_without_tests():
    files = ProcessingProviderPluginTemplate().template_files(FakeSpec())
    assert "my_plugin_algorithm.py" in files.values()
    assert "my_plugin_provider.py" in files.values()
    assert not any("test_" in v for v in files.values())


def test_processing_template_files_with_tests():
    files = ProcessingProviderPluginTemplate().template_files(FakeSpecWithTests())
    assert any("test_plugin_lifecycle.py" in v for v in files.values())


def test_processing_template_what_next_html():
    html = ProcessingProviderPluginTemplate().what_next_items_html(
        "/tmp/plugin", "my_plugin", ""
    )
    assert "my_plugin_algorithm.py" in html
    assert "Processing" in html


def test_processing_template_map(dialog):
    subframe = _select_template(dialog, 2)
    subframe.algo_name_text.setText("My Algorithm")
    subframe.algo_group_text.setText("My Group")
    subframe.provider_name_text.setText("My Provider")
    subframe.provider_descr_text.setText("Does things")
    result = ProcessingProviderPluginTemplate().template_map(FakeSpec(), dialog)
    assert result["TemplateAlgoName"] == "My Algorithm"
    assert result["TemplateAlgoGroup"] == "My Group"
    assert result["TemplateProviderName"] == "My Provider"
    assert result["TemplateProviderDescr"] == "Does things"
    assert result["TemplateHasProcessingProvider"] is True
