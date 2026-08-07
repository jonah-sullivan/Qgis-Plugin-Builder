# coding=utf-8
"""Tests for QGIS environment and core providers."""

import os

import pytest
from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry, QgsRasterLayer


def test_qgis_environment(qgis_app):
    """QGIS environment has the expected providers."""
    r = QgsProviderRegistry.instance()
    providers = r.providerList()
    if "gdal" not in providers:
        pytest.fail("gdal provider not found")
    if "ogr" not in providers:
        pytest.fail("ogr provider not found")


def test_projection(qgis_app):
    """QGIS can resolve a CRS from an authority code."""
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    if not crs.isValid():
        pytest.fail("EPSG:4326 did not resolve to a valid CRS")
    if crs.authid() != "EPSG:4326":
        pytest.fail(f"Expected authid EPSG:4326, got {crs.authid()}")


def test_raster_layer_crs(qgis_app):
    """A loaded raster layer has a valid CRS."""
    path = os.path.join(os.path.dirname(__file__), "tenbytenraster.asc")
    layer = QgsRasterLayer(path, "TestRaster")
    if not layer.isValid():
        pytest.fail(f"Raster layer at {path} is not valid")
    if not layer.crs().isValid():
        pytest.fail("Raster layer has an invalid CRS")
