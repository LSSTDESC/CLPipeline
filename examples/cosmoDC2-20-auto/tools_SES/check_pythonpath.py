#/usr/bin/python

import sys,os


sPythonPath=os.environ["PYTHONPATH"]
sNewPythonPath=""

for s in sPythonPath.split(":"):
    print s
    
    sRemoveLine="i686-slc4-gcc34-opt/lib/python2.5"

    if s[-len(sRemoveLine):]!=sRemoveLine: 
        sNewPythonPath=sNewPythonPath+s+":"

print "export PYTHONPATH="+sNewPythonPath[:-1]
    
    
