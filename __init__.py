"""
Package for using the CMSSW Tag and Probe CMSSW software. 
See documentation in http://devel.ifca.es/~duarte/pytnp_doc
"""
__revision__ = "$Id: __init__.py 36560 2004-07-18 06:16:08Z tim_one $"
#       python 2.6
import sys
if sys.version_info < (2,5):
	raise """\033[1;31mError: you must use python 2.6 or greater.\033[1;m
Check you have init the CMSSW environment: 
	$ cd /whereeverItIs/CMSSW/CMSSW_X_Y_Z/src
	$ cmsenv"""

# Importing the class
import libPytnp
import steerplots
#from libPytnp.pytnpclass import pytnp



