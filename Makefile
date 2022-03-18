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
#----------------------------------------------------------------------
all	: doc tar

#----------------------------------------------------------------------
doc	:
	@(cd $(DOCS_DIR); make)
#----------------------------------------------------------------------
tar	: clean
	@(cd ..; tar -czvf ${PACKAGE_DIR}-${VERSION}.tar.gz --exclude=".git" \
          ${PACKAGE_DIR})
#----------------------------------------------------------------------
python-api:
	@python setup.py build
#----------------------------------------------------------------------
#tests	:

#----------------------------------------------------------------------
clean	:
	$(shell $(RM_CMD))
#	@(cd ${DOCS_DIR}; make clean)

clobber	: clean
#	@(cd $(DOCS_DIR); make clobber)
	@rm -rf build dist ${PACKAGE_DIR}.egg-info
