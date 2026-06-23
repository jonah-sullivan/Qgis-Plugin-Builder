#!/bin/bash

QGIS_PREFIX_PATH=/usr
if [ -n "$1" ]; then
    QGIS_PREFIX_PATH=$1
fi

export QGIS_PREFIX_PATH=${QGIS_PREFIX_PATH}
export QGIS_PATH=${QGIS_PREFIX_PATH}
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib:${LD_LIBRARY_PATH}
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:${PYTHONPATH}

echo "QGIS PREFIX PATH: $QGIS_PREFIX_PATH"
export QGIS_DEBUG=0

export PATH=${QGIS_PREFIX_PATH}/bin:$PATH

echo "This script is intended to be sourced to set up your shell for"
echo "running tests against a QGIS installation at $QGIS_PREFIX_PATH"
echo
echo "To use it do:"
echo "source $BASH_SOURCE /your/optional/install/path"
echo
echo "Then use the make file supplied here e.g. make test"
