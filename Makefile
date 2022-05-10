#
# Makefile for the TFT Displays package.
#
# Development by Carl J. Nobile
#

include include.mk

TODAY		= $(shell date +"%Y-%m-%dT%H:%M:%S.%N%:z")
PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
DOCS_DIR	= $(PREFIX)/docs
RM_REGEX	= '(^.*.pyc$$)|(^.*.wsgic$$)|(^.*~$$)|(.*\#$$)|(^.*,cover$$)'
RM_CMD		= find $(PREFIX) -regextype posix-egrep -regex $(RM_REGEX) \
                  -exec rm {} \;
COVERAGE_FILE	= .coveragerc

#----------------------------------------------------------------------
all	: doc tar

.PHONY	: rpi-tests
rpi-tests: clean
	@rm -rf $(DOCS_DIR)/htmlcov
	@coverage erase --rcfile=$(COVERAGE_FILE)
	@export TFT_TESTING=True; \
        $${VIRTUAL_ENV}/bin/coverage run --rcfile=$(COVERAGE_FILE) \
                                     $${VIRTUAL_ENV}/bin/nosetests
	@coverage report --rcfile=$(COVERAGE_FILE)
	@coverage html --rcfile=$(COVERAGE_FILE)
	@echo $(TODAY)

.PHONY	: sphinx
sphinx	: clean
	(cd $(DOCS_DIR); make html)

#----------------------------------------------------------------------
.PHONY	: doc
doc	:
	@(cd $(DOCS_DIR); make)

#----------------------------------------------------------------------
.PHONY	: tar
tar	: clean
	@(cd ..; tar -czvf ${PACKAGE_DIR}-${VERSION}.tar.gz --exclude=".git" \
          ${PACKAGE_DIR})

#----------------------------------------------------------------------
.PHONY	: python-api
python-api:
	@python setup.py build

#----------------------------------------------------------------------
.PHONY	: clean
clean	:
	$(shell $(RM_CMD))
	@(cd ${DOCS_DIR}; make clean)

.PHONY	: clobber
clobber	: clean
	@rm -rf build dist ${PACKAGE_DIR}.egg-info
