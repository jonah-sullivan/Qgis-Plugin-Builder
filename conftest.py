# coding=utf-8
"""Make plugin_builder importable as part of a package during pytest runs.

plugin_builder.py and its siblings use relative imports (from .foo import Bar)
which require them to be loaded as part of a package. The project directory name
contains hyphens so it cannot serve as a Python package name directly. This
conftest registers the project root as a synthetic package named '_pluginbuilder'
and loads each module within that namespace, aliasing each to its bare name so
that 'from plugin_builder import PluginBuilder' works in the tests.
"""
import importlib.util
import os
import sys
import types

_PROJ = os.path.dirname(os.path.abspath(__file__))
_PKG = "_pluginbuilder"

_pkg = types.ModuleType(_PKG)
_pkg.__path__ = [_PROJ]
_pkg.__package__ = _PKG
sys.modules[_PKG] = _pkg


def _load_module(bare_name, filepath=None):
    full = f"{_PKG}.{bare_name}"
    if full in sys.modules:
        return sys.modules[full]
    path = filepath or os.path.join(_PROJ, f"{bare_name}.py")
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


# Load in dependency order so each relative import resolves correctly.
_load_module("plugin_specification")
_load_subpackage("plugin_templates", os.path.join(_PROJ, "plugin_templates"))
_load_module("select_tags_dialog")
_load_module("result_dialog")
_load_module("plugin_builder_dialog")
_load_module("plugin_builder")
