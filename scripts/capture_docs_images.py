#!/usr/bin/env python3
"""
Capture documentation screenshots for Plugin Builder.

Run from the repo root inside the qgis/qgis Docker container:

    QT_QPA_PLATFORM=offscreen python3 scripts/capture_docs_images.py

Or with a virtual framebuffer for native-looking rendering:

    Xvfb :99 -screen 0 1280x1024x24 &
    DISPLAY=:99 python3 scripts/capture_docs_images.py

Images that cannot be automated (require a live QGIS session) are noted below
and must be updated manually:
    - plugin_menu.png       (QGIS menu bar with plugin installed)
    - redundant_menu.png    (QGIS menu bar showing redundant name)
    - plugin_test.png       (QGIS running the generated plugin)
    - compile_failed.png    (compile error notification)
    - plugin_results.png    (results dialog after generation)
"""

import os
import sys

# ---------------------------------------------------------------------------
# Bootstrap QGIS — must happen before any qgis.PyQt imports
# ---------------------------------------------------------------------------
from qgis.core import QgsApplication

app = QgsApplication([], True)
QgsApplication.initQgis()

# ---------------------------------------------------------------------------
# Load the plugin package (mirrors conftest.py — repo dir has hyphens so it
# cannot be a Python package name; register it as a synthetic package instead)
# ---------------------------------------------------------------------------
import importlib.util
import types

repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_PKG = "_pluginbuilder"
_pkg = types.ModuleType(_PKG)
_pkg.__path__ = [repo_dir]
_pkg.__package__ = _PKG
sys.modules[_PKG] = _pkg


def _load_module(bare_name, filepath=None):
    full = f"{_PKG}.{bare_name}"
    if full in sys.modules:
        return sys.modules[full]
    path = filepath or os.path.join(repo_dir, f"{bare_name}.py")
    spec = importlib.util.spec_from_file_location(full, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = _PKG
    sys.modules[full] = mod
    sys.modules[bare_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_subpackage(bare_name, directory):
    full = f"{_PKG}.{bare_name}"
    pkg = types.ModuleType(full)
    pkg.__path__ = [directory]
    pkg.__package__ = full
    init = os.path.join(directory, "__init__.py")
    spec = importlib.util.spec_from_file_location(
        full, init, submodule_search_locations=[directory]
    )
    pkg.__spec__ = spec
    sys.modules[full] = pkg
    sys.modules[bare_name] = pkg
    spec.loader.exec_module(pkg)
    return pkg


_load_module("plugin_specification")
_load_subpackage("plugin_templates", os.path.join(repo_dir, "plugin_templates"))
_load_module("select_tags_dialog")
_load_module("result_dialog")
_load_module("plugin_builder_dialog")

from plugin_builder_dialog import PluginBuilderDialog  # noqa: E402

# ---------------------------------------------------------------------------
# Sample data — makes screenshots look realistic rather than blank
# ---------------------------------------------------------------------------
SAMPLE = {
    "class_name": "MyPlugin",
    "module_name": "my_plugin",
    "plugin_name": "My Plugin",
    "description": "A sample QGIS plugin",
    "version_number": "0.1",
    "qgis_minimum_version": "4.0",
    "qgis_maximum_version": "4.99",
    "author": "Jane Developer",
    "email": "jane@example.com",
    "about": (
        "This plugin does something useful with spatial data. "
        "It provides tools for analysing and visualising geographic information."
    ),
    "homepage": "https://github.com/example/my_plugin",
    "tracker": "https://github.com/example/my_plugin/issues",
    "repository": "https://github.com/example/my_plugin",
    "tags": "vector, analysis",
}

output_dir = os.path.join(repo_dir, "help", "source", "images")

# ---------------------------------------------------------------------------
# Build and populate the dialog
# ---------------------------------------------------------------------------
dialog = PluginBuilderDialog()
dialog.resize(600, 500)

for field, value in SAMPLE.items():
    widget = getattr(dialog, field, None)
    if widget is not None and hasattr(widget, "setText"):
        widget.setText(value)
    elif widget is not None and hasattr(widget, "setPlainText"):
        widget.setPlainText(value)

app.processEvents()

# ---------------------------------------------------------------------------
# Wizard pages → image filenames (index matches stackedWidget page order)
# ---------------------------------------------------------------------------
PAGES = [
    (0, "wizard_required_info.png"),
    (1, "wizard_about.png"),
    (2, "wizard_template.png"),
    (3, "wizard_helpers.png"),
    (4, "wizard_publication_info.png"),
    (5, "generating.png"),
]

dialog.show()
app.processEvents()

for index, filename in PAGES:
    dialog.stackedWidget.setCurrentIndex(index)
    app.processEvents()
    pixmap = dialog.grab()
    out_path = os.path.join(output_dir, filename)
    pixmap.save(out_path)
    print(f"Saved {out_path}")

dialog.hide()

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
QgsApplication.exitQgis()
print("\nDone. Update the following images manually (require a live QGIS session):")
print("  help/source/images/plugin_menu.png")
print("  help/source/images/redundant_menu.png")
print("  help/source/images/plugin_test.png")
print("  help/source/images/compile_failed.png")
print("  help/source/images/plugin_results.png")
