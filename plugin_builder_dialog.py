# coding=utf-8
"""
/***************************************************************************
    PluginBuilderDialog

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

import os
from string import capwords

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QFileInfo

try:
    Key_Escape = Qt.Key.Key_Escape
except AttributeError:
    Key_Escape = Qt.Key_Escape
from qgis.PyQt.QtWidgets import QMessageBox, QFrame, QDialog, QFileDialog
from .plugin_templates import templates

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "plugin_builder_dialog_base.ui")
)


class PluginBuilderDialog(QDialog, FORM_CLASS):
    """Dialog for defining the new plugin properties.

    Note we use multiple inheritance so you can reference any gui elements
    directly from this class without needing to go through self.ui and
    so that qt autoconnect slots work.

    """

    def __init__(self, parent=None, stored_output_path=""):
        """Constructor."""
        super(PluginBuilderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.template_subframe = None
        self.templates = templates()
        for templ in self.templates:
            self.template_cbox.addItem(templ.descr())
        self.update_prev_next_buttons()
        self.update_template()
        self.stackedWidget.currentChanged.connect(self.update_prev_next_buttons)
        self.next_button.clicked.connect(self.__next__)
        self.prev_button.clicked.connect(self.prev)
        self.template_cbox.currentIndexChanged.connect(self.update_template)
        self.btn_select_output.clicked.connect(self.select_directory)
        self.next_button.setFocus()
        self.output_directory.setText(stored_output_path)
        self.last_path = stored_output_path

    def update_prev_next_buttons(self):
        i = self.stackedWidget.currentIndex()
        self.prev_button.setEnabled(i > 0)

    def __next__(self):
        i = self.stackedWidget.currentIndex()
        if i < 6:
            ok = True
            if i == 0:
                ok = self.validate_entries()
            if i == 1:
                ok = self.validate_about()
            if i == 4:
                ok = self.validate_publication()
            if i == 5:
                ok = self.validate_output_directory()
            if ok:
                if i < 5:
                    self.stackedWidget.setCurrentIndex(i + 1)
                    if i == 4:
                        self.next_button.setText("Generate")
                        if self.output_directory.text() != "":
                            self.show_output_info(
                                os.path.join(
                                    self.output_directory.text(),
                                    self.module_name.text().lower(),
                                )
                            )
                else:
                    self.accept()

    def prev(self):
        i = self.stackedWidget.currentIndex()
        self.stackedWidget.setCurrentIndex(i - 1)
        if i - 1 != 5:
            self.next_button.setText("Next>")

    def template(self):
        return self.templates[self.template_cbox.currentIndex()]

    def update_template(self):
        if self.template_subframe is not None:
            self.template_subframe.setParent(None)
        subframe = QFrame(self.template_frame)
        self.frame_layout.addWidget(subframe, 1, 0, 1, 2)
        self.template_subframe = uic.loadUi(
            os.path.join(self.template().subdir(), "wizard_form_base.ui"), subframe
        )

    def validate_entries(self):
        """Check to see that all fields have been entered."""
        message = ""
        if (
            self.class_name.text() == ""
            or self.title.text() == ""
            or self.description.text() == ""
            or self.module_name.text() == ""
            or self.plugin_version.text() == ""
            or self.qgis_minimum_version.text() == ""
            or self.qgis_maximum_version.text() == ""
            or self.author.text() == ""
            or self.email_address.text() == ""
        ):
            message = "Some required fields are missing. " "Please complete the form.\n"

        def is_valid_version(v):
            parts = str(v).strip().split(".")
            return len(parts) >= 2 and all(p.isdigit() for p in parts)

        def version_tuple(v):
            return tuple(int(p) for p in str(v).strip().split("."))

        min_ver = self.qgis_minimum_version.text()
        max_ver = self.qgis_maximum_version.text()
        if (
            not is_valid_version(self.plugin_version.text())
            or not is_valid_version(min_ver)
            or (max_ver and not is_valid_version(max_ver))
        ):
            message += "Version numbers must be numeric.\n"

        elif max_ver and is_valid_version(max_ver) and is_valid_version(min_ver):
            if version_tuple(min_ver) >= version_tuple(max_ver):
                message += (
                    "Minimum QGIS version must be less than the maximum version.\n"
                )

        # validate plugin name
        # check that we have only ascii char in class name
        if not all(ord(c) < 128 for c in self.class_name.text()):
            self.class_name.setText(
                str(self.class_name.text()).encode("ascii", "ignore")
            )
            message += (
                "The Class name must be ASCII characters only, "
                "the name has been modified for you. \n"
            )
        # check space and force CamelCase
        if str(self.class_name.text()).find(" ") > -1:
            class_name = capwords(str(self.class_name.text()))
            self.class_name.setText(class_name.replace(" ", ""))
            message += (
                "The Class name must use CamelCase. "
                "No spaces are allowed; the name has been modified for you."
            )
        # noinspection PyArgumentList
        if message != "":
            QMessageBox.warning(self, "Information missing or invalid", message)
        else:
            if self.last_path:
                self.lbl_full_output_path.setText(
                    os.path.join(self.last_path, self.module_name.text())
                )
            return True

    def validate_about(self):
        if len(self.about.toPlainText()) == 0:
            QMessageBox.warning(
                self,
                "Missing About",
                "Please enter a bit of detail about your plugin "
                "(purpose, function, requirements, etc.).\n\n"
                "You can modify this later by editing the 'about' tag in the "
                "generated metadata.txt file.",
            )
            return False
        else:
            return True

    def validate_publication(self):
        url_tracker = self.tracker.text()
        url_repo = self.repository.text()
        if not url_tracker or not url_repo:
            QMessageBox.warning(
                self,
                "Missing Tracker/Repository",
                "A bug tracker and repository entry are now required. "
                "You may enter placeholders here, but will need valid "
                "entries prior to submitting your plugin to the QGIS "
                "plugin repository.",
            )
            return False
        elif not (url_tracker.startswith("http://") or url_tracker.startswith("https://")) or \
                not (url_repo.startswith("http://") or url_repo.startswith("https://")):
            QMessageBox.warning(
                self,
                "Malformed URL(s)",
                "Your tracker and repository URLs must begin with http:// or https://. "
                "Use a fully qualified URL.",
            )
            return False
        return True

    def select_directory(self):
        plugin_path = QFileDialog.getExistingDirectory(
            self, "Select the Directory for your Plugin", self.last_path
        )
        self.output_directory.setText(plugin_path)
        full_output = os.path.join(plugin_path, self.module_name.text().lower())
        self.lbl_full_output_path.setText(
            os.path.join(plugin_path, self.module_name.text().lower())
        )
        self.show_output_info(full_output)

    def show_output_info(self, full_output):
        if QFileInfo(full_output).exists():
            self.lbl_full_output_path.setText(
                full_output + "\nYour plugin will overwrite the existing contents!"
            )
            self.lbl_full_output_path.setStyleSheet(
                "QLabel { color : red;  font-weight : bold;}"
            )
        else:
            self.lbl_full_output_path.setStyleSheet("QLabel { color : black; }")

    def validate_output_directory(self):
        good_dir = False
        if len(self.output_directory.text()) > 0:
            if QFileInfo(self.output_directory.text()).exists():

                if QFileInfo(self.output_directory.text()).isWritable():
                    good_dir = True
                else:
                    msg = "Your output directory is write-protected."
            else:
                msg = "Your output directory does not exist."

        else:
            msg = "Please select an output directory."

        if not good_dir:
            QMessageBox.warning(None, "Error", msg)

        return good_dir

    def keyPressEvent(self, event):
        # prevent escape from closing the dialog
        if event.key() == Key_Escape:
            # QDialog.keyPressEvent(event)
            pass