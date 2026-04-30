# coding=utf-8
"""Tests for QGIS environment and core providers."""

import os

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry, QgsRasterLayer


def test_qgis_environment(qgis_app):
    """QGIS environment has the expected providers."""
    r = QgsProviderRegistry.instance()
    assert "gdal" in r.providerList()
    assert "ogr" in r.providerList()


def test_projection(qgis_app):
    """QGIS can resolve a CRS from an authority code."""
    crs = QgsCoordinateReferenceSystem("EPSG:4326")
    assert crs.isValid()
    assert crs.authid() == "EPSG:4326"


def test_raster_layer_crs(qgis_app):
    """A loaded raster layer has a valid CRS."""
    path = os.path.join(os.path.dirname(__file__), "tenbytenraster.asc")
    layer = QgsRasterLayer(path, "TestRaster")
    assert layer.isValid()
    assert layer.crs().isValid()
