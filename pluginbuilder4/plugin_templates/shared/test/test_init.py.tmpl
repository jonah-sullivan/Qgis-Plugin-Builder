# coding=utf-8
"""Tests that metadata.txt contains all fields required by plugins.qgis.org."""

import configparser
from pathlib import Path

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
    file_path = Path(__file__).parent.parent / "metadata.txt"
    parser = configparser.ConfigParser()
    parser.optionxform = str
    parser.read(file_path)
    assert parser.has_section("general"), (
        f'Cannot find a section named "general" in {file_path}'
    )
    present = dict(parser.items("general"))
    for field in REQUIRED_METADATA:
        assert field in present, f'Cannot find metadata "{field}" in {file_path}'
