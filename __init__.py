"""pytnp

pytnp package for using the CMSSW Tag and Probe package.
See documentation in $WEB$

"""
__revision__ = "$Id: __init__.py 36560 2004-07-18 06:16:08Z tim_one $"
#       python 2.6
import sys
if sys.version_info < (2,6):
	raise """\033[1;31mError: you must use python 2.6 or greater.\033[1;m
Check you have init the CMSSW environment: 
	$ cd /whereeverItIs/CMSSW/CMSSW_X_Y_Z/src
	$ cmsenv"""

# Importing the class
import libPytnp
#from libPytnp.pytnpclass import pytnp



