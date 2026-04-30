#/***************************************************************************
#    PluginBuilder
#
#    Creates a QGIS plugin template for use as a starting point in plugin
#    development.
#                             -------------------
#        begin                : 2011-01-20
#        git sha              : $Format:%H$
#        copyright            : (C) 2011 by GeoApt LLC
#        email                : gsherman@geoapt.com
# ***************************************************************************/
#
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/
# Makefile for a PyQGIS plugin
#

QGISDIR=$(shell python3 -c "import sys; sys.path.insert(0, '.'); import qgis_dirs; print(qgis_dirs.deployment_dir)")

PLUGINNAME=pluginbuilder4

PY_FILES = plugin_builder.py plugin_builder_dialog.py result_dialog.py __init__.py plugin_specification.py select_tags_dialog.py qgis_dirs.py

UI_FILES = plugin_builder_dialog_base.ui results_dialog_base.ui select_tags_dialog_base.ui

TEMPLATE_DIR = plugin_templates

EXTRAS = icon.png metadata.txt taglist.txt

HELP_BUILD = help/build/html/*

# The deploy target copies plugin files to the QGIS plugins directory
deploy:
	mkdir -p $(QGISDIR)/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(QGISDIR)/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(QGISDIR)/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(QGISDIR)/$(PLUGINNAME)
	cp -rvf $(TEMPLATE_DIR) $(QGISDIR)/$(PLUGINNAME)

# remove the deployed plugin
dclean:
	rm -rf $(QGISDIR)/$(PLUGINNAME)

zip: dclean deploy
	rm -f $(PLUGINNAME).zip
	cd $(QGISDIR); zip -9vr $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)


# Create a zip package. Requires passing a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
# Get the last commit hash
COMMITHASH=$(shell git rev-parse HEAD)
package:
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(COMMITHASH)
		@echo "Created package: $(PLUGINNAME).zip"

clean:
	rm -f $(PLUGINNAME).zip

test: compile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		python -m pytest -v || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error:"
	@echo "  Linux/Mac: source run-env-linux.sh <path to qgis install>; make test"
	@echo "  Windows:   activate your OSGeo4W-based venv and run make test from Git Bash"
	@echo "----------------------"



pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude pydev,resources.py,conf.py . || true
