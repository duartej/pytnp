"""
Simple module with only a function to extract the identifier (pytnpname) and the 
latex description of a root file
"""
from management import printError, printWarning, parserConfig


def getResName( aFile, **keywords ):
	""".. function:: getResName( fileName[, config=configfile] ) -> pytnpname,latexstring

	Extract from file name, T&P-like, the resonance
	and returns it plain and in Latex format.

	:param fileName: the root file name
	:type fileName: string
	:keyword config: configuration file to impose the results of this function. 
	                 Makes use of the ``DataNames`` dictionary placed
	:type config: string

	:return: unique identifier (pytnpname) and latex description of this root file
	:rtype: tuple of strings
	
	.. warning::
	   This function is highly dependent of the name of the file (if you don't use a config file).
	   Standard Format:  NameOFResonance_X_blabla.root
	
	:raise KeyError: keyword erroneous
	:raise TypeError: no config file provided and no root file name in standard format
	:raise RuntimeError: somethin wrong happens. Warn to developers

	.. note::
	   Probably will change to ``tnputils`` module
	"""
	import re

	regexp = re.compile( '\D*(?P<NUMBER>\dS)' ) 
	resonance = ''
	resonanceLatex = ''
	# Hardcoded dict: include here new resonances 
	nameDict = { 'JPsi' : ('J/#Psi','JPsi'),
			'Upsilon': ('All #Upsilon','AllUpsilons'),
			'Z' : ('Z#rightarrow#mu#mu','Z')
			}
	# Complements
	adjectDict = { 'DATA' : (' Data', '_DATA'),
			'ReWeight' : (' ReWeight ', '_ReWeight'),
			'GoodCowboys' : (' GCS', '_GoodCowboysAndSeagulls'),
			'_MC_' : (' MC', ''),
			'_Spring10_' : (' MC', ''),
			}
	#-- Add and/or updating the keys, entered by the user
	isDone = False
	for key, _file in keywords.iteritems():
		if key != 'config':
			message = "Invalid argument key '%s', only accepted 'config" % key
			printError( getResName.__module__+'.'+getResName.__name__, message, KeyError )
		#-- Controlling the None case
		if _file:
			for name, value in parserConfig( keywords['config'], 'DataNames' ).iteritems():
				nameDict[name] = value
				isDone = True
			# User rules, so...
			# Posible try!! FIXME!!
			resonanceLatex = nameDict[aFile][0]
			resonance = nameDict[aFile][1]
			return resonance,resonanceLatex

	try:
		num = regexp.search( aFile ).group( 'NUMBER' )
		resonanceLatex = '#Upsilon('+num+')'
		resonance = 'Upsilon'+num

	except AttributeError:
		#Reverse sorted to assure DATA is the last one
		for name, (resLatex,res) in sorted(nameDict.iteritems(),reverse=True):
			if aFile.find( name ) != -1:
				resonanceLatex = resLatex
				resonance = res
		if resonance == '':
			message ="""This function is highly dependent of the \n"""\
					"""name of the file, you need an standard format like:\n"""\
					"""    NameOFResonance_X_blabla.root"""\
					"""Unrecognized name: \033[1;m\033[1;39m  '%s'\033[1;m""" % aFile
			printError( getResName.__module__+'.'+getResName.__name__, message, TypeError )
		
	except:
		message ="""UNEXPECTED ERROR!! Send a e-mail to the developer(s) with all information\n"""\
				"""needed to reproduce this error"""
		printError( getresname.__module__+'.'+getresname.__name__, message, RuntimeError )
	
	#All work is done
	if isDone:
		return resonance, resonanceLatex
	
	#Including others..
	# FIXME: To be DEPRECATED
	for name, (resLatex,res) in sorted(adjectDict.iteritems(),reverse=True):
		if aFile.find( name ) != -1:
			resonanceLatex += resLatex
			resonance += res

	return resonance,resonanceLatex
