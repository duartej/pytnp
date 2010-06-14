"""pytnp

pytnp package for using the CMSSW Tag and Probe package.
See documentation in $WEB$

"""
__revision__ = "$Id: __init__.py 36560 2004-07-18 06:16:08Z tim_one $"
#TODO: Funcion que comprueba si estoy utilizando 
#       python 2.6

#FIXME: Quitarlo despues de rectificar referencias pytnp.ROOT en effPlots
import ROOT
# Importing the class
from pytnpclass import pytnp

#No se si lo dejare
from utils.tnputils import *
from utils.getresname import *

