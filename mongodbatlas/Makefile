#
# Makefile for AtlasAPI Project
#
# Author : Joe.Drumgoole@mongodb.com
#

ROOT=${HOME}/GIT/atlasapi

organizations:
	(export PYTHONPATH=${ROOT};cd ${ROOT}/atlasapi;pipenv shell; \
	python ${ROOT}/atlasapi/atlascli.py --list orgs)

pause_cluster:
	(export PYTHONPATH=${ROOT};cd ${ROOT}/atlasapi;pipenv shell; python ${ROOT}/atlasapi/atlascli.py --org_id ${ATLAS_ORGANIZATION})

test:
	pytest
