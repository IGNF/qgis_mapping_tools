#/***************************************************************************
# MappingTools
#
# Data acquisition tools from vector segmentation layers
#							 -------------------
#		begin				: 2015-05-05
#		git sha				: $Format:%H$
#		copyright			: (C) 2015 by IGN
#		email				: carhab@ign.fr
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


#Add iso code for any locales you want to support here (space separated)
# default is no locales
# LOCALES = af
LOCALES =

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease
#LRELEASE = lrelease
#LRELEASE = lrelease-qt4

PLUGINNAME = MappingTools3

PY_FILES = \
	src/mapping_tools.py \
	src/import_feature.py \
	src/fusion.py \
	src/custom_action.py \
	src/custom_maptool.py \
	src/__init__.py

UI_FILES = sourcelayerselector.ui

EXTRAS = img/fusion_icon.png img/import_feature_icon.png metadata.txt

COMPILED_RESOURCE_FILES = resources.py sourcelayerselector.py

PEP8EXCLUDE=pydev,resources.py,conf.py,third_party,ui


#################################################
# Normally you would not need to edit below here
#################################################

HELP = help/build/html

PLUGIN_UPLOAD = $(c)/plugin_upload.py

RESOURCE_SRC=$(shell grep '^ *<file' resources/resources.qrc | sed 's@</file>@@g;s/.*>//g' | tr '\n' ' ')

QGISDIR=.local/share/QGIS/QGIS3/profiles/default

default: compile

compile: $(COMPILED_RESOURCE_FILES)

%.py : %.qrc $(RESOURCES_SRC)
	pyrcc5 -o $*.py $<

%.py : %.ui $(RESOURCES_SRC)
	pyuic5 -o $*.py $<

%.qm : %.ts
	$(LRELEASE) $<

test: deploy
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"
	qgis --defaultui --code test/src/testMappingTools.py

deploy: compile
	@echo
	@echo "------------------------------------------"
	@echo "Deploying plugin to your .qgis2 directory."
	@echo "------------------------------------------"
	# The deploy  target only works on unix like operating system where
	# the Python plugin directory is located at:
	# $HOME/$(QGISDIR)/python/plugins
	mkdir -p $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(COMPILED_RESOURCE_FILES) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr i18n $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)
	#cp -vfr $(HELP) $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also deletes any .git entry
dclean:
	@echo
	@echo "-----------------------------------"
	@echo "Removing any compiled python files."
	@echo "-----------------------------------"
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME) -iname ".git" -prune -exec rm -Rf {} \;


derase:
	@echo
	@echo "-------------------------"
	@echo "Removing deployed plugin."
	@echo "-------------------------"
	rm -Rf $(HOME)/$(QGISDIR)/python/plugins/$(PLUGINNAME)

zip: deploy dclean
	@echo
	@echo "---------------------------"
	@echo "Creating plugin zip bundle."
	@echo "---------------------------"
	# The zip target deploys the plugin and creates a zip file with the deployed
	# content. You can then upload the zip file on http://plugins.qgis.org
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/$(QGISDIR)/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

package: compile
	# Create a zip package of the plugin named $(PLUGINNAME).zip.
	# This requires use of git (your plugin development directory must be a
	# git repository).
	# To use, pass a valid commit or tag as follows:
	#   make package VERSION=Version_0.3.2
	@echo
	@echo "------------------------------------"
	@echo "Exporting plugin to zip package.	"
	@echo "------------------------------------"
	rm -f $(PLUGINNAME).zip
	git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
	echo "Created package: $(PLUGINNAME).zip"

upload: zip
	@echo
	@echo "-------------------------------------"
	@echo "Uploading plugin to QGIS Plugin repo."
	@echo "-------------------------------------"
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

transup:
	@echo
	@echo "------------------------------------------------"
	@echo "Updating translation files with any new strings."
	@echo "------------------------------------------------"
	@chmod +x scripts/update-strings.sh
	@scripts/update-strings.sh $(LOCALES)

transclean:
	@echo
	@echo "------------------------------------"
	@echo "Removing compiled translation files."
	@echo "------------------------------------"
	rm -f i18n/*.qm

clean:
	@echo
	@echo "------------------------------------"
	@echo "Removing uic and rcc generated files"
	@echo "------------------------------------"
	#rm $(COMPILED_UI_FILES) $(COMPILED_RESOURCE_FILES)
	rm resources.py
	rm  *.pyc test/src/*.pyc



pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc . || true
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128 --exclude $(PEP8EXCLUDE) . || true
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)
