# coding=utf-8
"""
/***************************************************************************
    ResultDialog

    Creates a skeleton QGIS plugin for use as a starting point
                             -------------------
        begin                : 2011-01-20
        git sha              : $Format:%H$
        copyright            : (C) 2011-2026 by Gary Sherman, 2026 Jonah Sullivan
        email                : gsherman@geoapt.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from pathlib import Path
from typing import Any

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QTextBrowser, QWidget

FORM_CLASS: Any
FORM_CLASS, _ = uic.loadUiType(str(Path(__file__).parent / "results_dialog_base.ui"))


class ResultDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog for showing the results of the plugin creation process."""

    # Widgets created by setupUi() from results_dialog_base.ui
    web_view: QTextBrowser

    def __init__(self, parent: QWidget | None = None) -> None:
        super(ResultDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)

        # Prevent QTextBrowser from trying to navigate internally
        self.web_view.setOpenLinks(False)
        # Open all clicked links via the OS (file explorer, browser, etc.)
        self.web_view.anchorClicked.connect(self._open_url)

    def _open_url(self, url: QUrl) -> None:
        QDesktopServices.openUrl(url)
