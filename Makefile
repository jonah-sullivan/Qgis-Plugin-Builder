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

DOTQGIS=.qgis3

PLUGINNAME=pluginbuilder3

PY_FILES = plugin_builder.py plugin_builder_dialog.py result_dialog.py __init__.py plugin_specification.py select_tags_dialog.py

UI_FILES = plugin_builder_dialog_base.ui results_dialog_base.ui select_tags_dialog_base.ui

TEMPLATE_DIR = plugin_templates

EXTRAS = icon.png plugin_builder.png metadata.txt taglist.txt

HELP_BUILD = help/build/html/*

RESOURCE_FILES = resources.py
PY_UI_FILES = $(UI_FILES:.ui=.py)

default: compile

compile: $(PY_UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	rcc -o $@ $<

%.py : %.ui
	pyuic6 -o $@ $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/$(DOTQGIS)/python/plugins
deploy: compile
	mkdir -p $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)/help
	cp -vf $(PY_FILES) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	cp -vf $(RESOURCE_FILES) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	cp -rvf $(TEMPLATE_DIR) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)
	cp -rvf $(HELP_BUILD) $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)/help

# remove the deployed plugin
dclean:
	rm -rf $(HOME)/$(DOTQGIS)/python/plugins/$(PLUGINNAME)

zip: dclean deploy
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(DOTQGIS)/python/plugins; zip -9vr $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)


# Create a zip package. Requires passing a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
# Get the last commit hash
COMMITHASH=$(shell git rev-parse HEAD)
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(COMMITHASH)
		@echo "Created package: $(PLUGINNAME).zip"

clean:
	rm $(RESOURCE_FILES)

test: compile
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		nosetests -v --with-id --with-coverage --cover-package=. \
		3>&1 1>&2 2>&3 3>&- || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
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
