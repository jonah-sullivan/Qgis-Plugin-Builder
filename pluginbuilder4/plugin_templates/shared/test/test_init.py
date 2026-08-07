# coding=utf-8
"""Tests that metadata.txt contains all fields required by plugins.qgis.org."""

import configparser
import os

import pytest

REQUIRED_METADATA = [
    "name",
    "description",
    "version",
    "qgisMinimumVersion",
    "email",
    "author",
    "tracker",
    "repository",
]


def test_metadata_has_required_fields():
    """metadata.txt has all fields required by plugins.qgis.org."""
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "metadata.txt")
    )
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(file_path)
    if not parser.has_section("general"):
        pytest.fail(f'Cannot find a section named "general" in {file_path}')
    present = dict(parser.items("general"))
    for field in REQUIRED_METADATA:
        if field not in present:
            pytest.fail(f'Cannot find metadata "{field}" in {file_path}')
