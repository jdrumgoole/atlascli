#
# Makefile for AtlasAPI Project
#
# Author : Joe.Drumgoole@mongodb.com
#

ROOT=${HOME}/GIT/atlasapi
PYTHON=python3

test_cli:
	python atlascli\atlascli.py -h
	python atlascli\atlascli.py -l -lp -lc

test:
	nosetests

prod_build:clean  sdist
	twine upload --verbose dist/* -u jdrumgoole

test_build:test sdist
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

test_install:
	pip3 install --index-url https://test.pypi.org/simple/ atlascli


sdist:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist atlascli.egg-info
	pip3 uninstall atlascli

keyring:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole
