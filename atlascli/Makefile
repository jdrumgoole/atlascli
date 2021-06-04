# We run resume twice to test the code path after a cluster has been resumed
all: help noargs list listproj defaultcluster

help:
	python main.py -h  > makefile.log 2>&1

noargs:
	python main.py > makefile.log 2>&1

list:
	python main.py -l > makefile.log 2>&1

listcluster:
	python main.py -lc > makefile.log 2>&1

listproj:
	python main.py -lp > makefile.log 2>&1

defaultcluster:
	python main.py --defaultcluster > makefile.log 2>&1

# because resumed clusters can't immediately be paused (takes an hour) we
# can't run automated pause resume

resume:
	python main.py -r GDELT 

pause:
	python main.py -p GDELT  2>&1 > makefile.log
	
resumedelay:
	python main.py -r GDELT  
	sleep 3601
	python main.py -p GDELT