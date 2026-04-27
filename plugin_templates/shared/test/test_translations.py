# coding=utf-8
"""Safe Translations Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from .utilities import get_qgis_app

__author__ = "ismailsunni@yahoo.co.id"
__date__ = "12/10/2011"
__copyright__ = "Copyright 2012, Australia Indonesia Facility for " "Disaster Reduction"
import unittest
import os

from qgis.PyQt.QtCore import QTranslator

QGIS_APP = get_qgis_app()


class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if "LANG" in iter(os.environ.keys()):
            os.environ.__delitem__("LANG")

    def tearDown(self):
        """Runs after each test."""
        if "LANG" in iter(os.environ.keys()):
            os.environ.__delitem__("LANG")

    def test_qgis_translations(self):
        """Test that translations work."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        i18n_dir = os.path.join(dir_path, "i18n")
        qm_files = [f for f in os.listdir(i18n_dir) if f.endswith(".qm")] if os.path.isdir(i18n_dir) else []
        if not qm_files:
            self.skipTest('No .qm files found — run "make" to compile translations first')
        translator = QTranslator()
        self.assertTrue(translator.load(os.path.join(i18n_dir, qm_files[0])), f"Failed to load {qm_files[0]}")


if __name__ == "__main__":
    unittest.main()
