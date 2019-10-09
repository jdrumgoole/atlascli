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
	pipenv run twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build:test sdist
	pipenv run twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

sdist:
	pipenv run setup.py sdist

keyring:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole
