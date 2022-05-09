#!/bin/bash
#
# Run a single test file with coverage.
#

PREFIX=$(pwd)
COVERAGE_FILE=.coveragerc
VE_BIN=$VIRTUAL_ENV/bin
coverage erase --rcfile=${COVERAGE_FILE}
export TFT_TESTING=True
${VE_BIN}/coverage run --rcfile=${COVERAGE_FILE} ${VE_BIN}/nosetests $1
coverage report -m --rcfile=${COVERAGE_FILE}
