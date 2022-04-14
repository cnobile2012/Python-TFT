#
# Makefile for the TFT Displays package.
#
# Development by Carl J. Nobile
#

include include.mk

PREFIX		= $(shell pwd)
PACKAGE_DIR	= $(shell echo $${PWD\#\#*/})
DOCS_DIR	= $(PREFIX)/docs
RM_REGEX	= '(^.*.pyc$$)|(^.*.wsgic$$)|(^.*~$$)|(.*\#$$)|(^.*,cover$$)'
RM_CMD		= find $(PREFIX) -regextype posix-egrep -regex $(RM_REGEX) \
                  -exec rm {} \;
RPI_TEST_PATH	= $(PREFIX)/ILI9225 $(PREFIX)/ILI9341 $(PREFIX)/fonts \
                  $(PREFIX)/utils $(PREFIX)/fonts \
                  $(PREFIX)/py_versions/raspberrypi.py

#----------------------------------------------------------------------
all	: doc tar

.PHONY	: tests
rpi-tests: clean
	@nosetests --with-coverage --cover-erase --cover-inclusive \
                   --cover-html --cover-html-dir=$(DOCS_DIR)/htmlcov \
                   --cover-package=ILI9225 --cover-package=ILI9341 \
                   --cover-package=py_versions --cover-package=utils \
                   $(RPI_TEST_PATH)

#.PHONY	: sphinx
#sphinx	: clean
#	(cd $(DOCS_DIR); make html)

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
