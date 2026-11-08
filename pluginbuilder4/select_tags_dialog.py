# coding=utf-8
"""
/***************************************************************************
    SelectTagsDialog

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
from qgis.PyQt.QtWidgets import QListView, QWidget

FORM_CLASS: Any
FORM_CLASS, _ = uic.loadUiType(
    str(Path(__file__).parent / "select_tags_dialog_base.ui")
)


class SelectTagsDialog(QtWidgets.QDialog, FORM_CLASS):
    """Dialog for selecting one or more tags for the plugin."""

    # Widgets created by setupUi() from select_tags_dialog_base.ui
    listView: QListView  # noqa: N815 - name set in the .ui file

    def __init__(self, parent: QWidget | None = None) -> None:
        super(SelectTagsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
