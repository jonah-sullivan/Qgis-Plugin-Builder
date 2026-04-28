# coding=utf-8
"""Tests for translation loading."""

import os

import pytest
from qgis.PyQt.QtCore import QCoreApplication, QTranslator


def test_qgis_translations(qgis_app):
    """Translation files load and translate strings correctly."""
    parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
    dir_path = os.path.abspath(parent_path)
    file_path = os.path.join(dir_path, "i18n", "af.qm")
    if not os.path.isfile(file_path):
        pytest.skip('af.qm not found — run "make transcompile" first')
    translator = QTranslator()
    assert translator.load(file_path), "Failed to load af.qm"
    QCoreApplication.installTranslator(translator)
    assert QCoreApplication.translate("@default", "Good morning") == "Goeie more"
