# coding=utf-8
"""Tests for translation loading."""

from pathlib import Path

import pytest
from qgis.PyQt.QtCore import QCoreApplication, QTranslator


def test_qgis_translations(qgis_app):
    """Translation files load and translate strings correctly."""
    parent_path = Path(__file__).parent.parent
    dir_path = parent_path.absolute()
    file_path = dir_path / "i18n" / "af.qm"
    if not file_path.exists():
        pytest.skip('af.qm not found — run "make transcompile" first')
    translator = QTranslator()
    assert translator.load(str(file_path)), "Failed to load af.qm"
    QCoreApplication.installTranslator(translator)
    translated = QCoreApplication.translate("@default", "Good morning")
    assert translated == "Goeie more", f"Expected 'Goeie more', got {translated!r}"
