#
# Makefile for AtlasAPI Project
#
# Author : Joe.Drumgoole@mongodb.com
#

ROOT=${HOME}/GIT/atlasapi
PYTHON=python3

test:
	nosetests

prod_build:clean  sdist
	twine upload --verbose dist/* -u jdrumgoole

test_build:test sdist
	twine upload --verbose dist/* -u jdrumgoole

sdist:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbatlas.egg-info

keyring:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole
