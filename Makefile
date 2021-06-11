#
# Makefile for AtlasAPI Project
#
# Author : Joe.Drumgoole@mongodb.com
#

ROOT=${HOME}/GIT/atlasapi
PYTHON=python3

testcli:
	(cd atlascli;make)

nosetest:
	nosetests

test: nosetest testcli
	echo "Tests completed"

prod_build:clean  sdist
	twine upload --verbose dist/* -u jdrumgoole

twine_test_test: sdist
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

twine_prod_test: sdist
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
