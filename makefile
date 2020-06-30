#!/bin/bash

export REQ_DIR = requirements
export LIB_REQ = ${REQ_DIR}/lib_requirements.txt
export DEP_REQ = ${REQ_DIR}/deploy_requirements.txt
export PROJECT_DIR = rsterm
export TEST_DIR = tests


#############################################################
#              Commands for Python environment              #
#############################################################

lib_init:
	if [[ -d ./venv ]]; then rm -rf venv; fi \
	&& python3.6 -m venv venv \
	&& . venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel \
	&& pip install -r ${LIB_REQ}


deployment_init:
	if [[ -d ./venv ]]; then rm -rf venv; fi \
	&& python3.6 -m venv venv \
	&& . venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel \
	&& pip install -r ${DEP_REQ}


req:
	rm -f ${LIB_REQ} \
	&& . venv/bin/activate \
	&& pip freeze | grep 'flake8\|mccabe\|pycodestyle\|zipp\|pyflakes\|importlib-metadata\|rsterm' -v > ${LIB_REQ}


depreq:
	rm -f ${DEP_REQ} \
	&& . venv/bin/activate \
	&& pip freeze | grep 'rsterm' -v > ${DEP_REQ}


update:
	. venv/bin/activate \
	&& pip install --upgrade pip setuptools wheel


install:
	pip install -e .

#############################################################
#              Commands for testing                         #
#############################################################


lint:
	. venv/bin/activate \
	&& python -m flake8 ${PROJECT_DIR} ${TEST_DIR}

test:
	. venv/bin/activate \
	&& python -m unittest discover -v ${TEST_DIR}

qa:
	make test
	make lint


#############################################################
#              Build and Distribution                       #
#############################################################

build:
	. venv/bin/activate \
	&& python setup.py sdist bdist_wheel

deploy:
  ifdef version
		./bin/release --version $(version)
  else
	  ./bin/release
  endif
