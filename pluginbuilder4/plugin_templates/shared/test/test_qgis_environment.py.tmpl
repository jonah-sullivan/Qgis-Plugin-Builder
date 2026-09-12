# coding=utf-8
"""Tests for QGIS environment and core providers."""

import os

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry, QgsRasterLayer


def test_qgis_environment(qgis_app):
    """QGIS environment has the expected providers."""
    r = QgsProviderRegistry.instance()
    providers = r.providerList()
    assert "gdal" in providers, "gdal provider not found"
    assert "ogr" in providers, "ogr provider not found"


def test_projection(qgis_app):
    """QGIS can resolve a CRS from an authority code."""
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    assert crs.isValid(), "EPSG:4326 did not resolve to a valid CRS"
    assert crs.authid() == "EPSG:4326", f"Expected authid EPSG:4326, got {crs.authid()}"


def test_raster_layer_crs(qgis_app):
    """A loaded raster layer has a valid CRS."""
    path = os.path.join(os.path.dirname(__file__), "tenbytenraster.asc")
    layer = QgsRasterLayer(path, "TestRaster")
    assert layer.isValid(), f"Raster layer at {path} is not valid"
    assert layer.crs().isValid(), "Raster layer has an invalid CRS"
