#
# Makefile for AtlasAPI Project
#
# Author : Joe.Drumgoole@mongodb.com
#

ROOT=${HOME}/GIT/atlasapi
PYTHON=python3

test_cli:
	python mongodbatlas\atlascli.py -h
	python mongodbatlas\atlascli.py -l -lp -lc

test:
	nosetests

prod_build:clean  sdist
	twine upload --verbose dist/* -u jdrumgoole

test_build:test sdist
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

test_install:
	pip3 install --index-url https://test.pypi.org/simple/ mongodbatlas


sdist:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbatlas.egg-info
	pip3 uninstall mongodbatlas

keyring:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole
