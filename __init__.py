"""pytnp

pytnp package for using the CMSSW Tag and Probe package.
See documentation in $WEB$

"""
__revision__ = "$Id: __init__.py 36560 2004-07-18 06:16:08Z tim_one $"
#TODO: Funcion que comprueba si estoy utilizando 
#       python 2.6
import sys
if sys.version_info < (2,6):
	raise """\033[1;31mError: you must use python 2.6 or greater.\033[1;m
Check you have init the CMSSW environment: 
	$ cd /whereeverItIs/CMSSW/CMSSW_X_Y_Z/src
	$ cmsenv"""

#FIXME: Quitarlo despues de rectificar referencias pytnp.ROOT en effPlots
import ROOT
# Importing the class
from pytnpclass import pytnp

#No se si lo dejare
from utils.tnputils import *
from utils.getresname import *


