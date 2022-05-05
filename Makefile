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
RUN_TESTS	= 1

#----------------------------------------------------------------------
all	: doc tar

.PHONY	: rpi-tests
rpi-tests: clean
	@rm -rf $(DOCS_DIR)/htmlcov
	@nosetests --with-coverage --cover-erase --nocapture --nologcapture \
                   --processes=-1 \
                   --cover-package=$(PREFIX)/ILI9225 \
                   --cover-package=$(PREFIX)/ILI9341 \
                   --cover-package=$(PREFIX)/utils \
                   --cover-package=$(PREFIX)/fonts \
                   --cover-package=$(PREFIX)/py_versions/raspberrypi.py
#                   --cover-inclusive \
#                   --cover-html --cover-html-dir=$(DOCS_DIR)/htmlcov
#	coverage combine
#	coverage report
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
#	@(cd ${DOCS_DIR}; make clean)

.PHONY	: clobber
clobber	: clean
#	@(cd $(DOCS_DIR); make clobber)
	@rm -rf build dist ${PACKAGE_DIR}.egg-info
