"""
"""
from management import printError, printWarning, parserConfig


def getResName( aFile, **keywords ):
	"""
	getResName( fileName[, 'config=config_file.py'] ) -> str,str (latex)

	Extract from file name, T&P-like, the resonance
	and returns it plain and in Latex format.
	
	Warning: This function is highly dependent
	of the name of the file-- 
	Standard Format:  NameOFResonance_X_blabla.root
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
	for key, _file in keywords.iteritems():
		if key != 'config':
			message = "Invalid argument key '%s', only accepted 'config" % key
			printError( getResName.__module__+'.'+getResName.__name__, message, KeyError )
		for name, value in parserConfig( keywords['config'], 'DataNames' ).iteritems():
			nameDict[name] = value

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
			printWarning( getResName.__module__+'.'+getResName.__name__, message )
			return None
		
	except:
		message ="""UNEXPECTED ERROR!! Send a e-mail to the developer(s) with all information\n"""\
				"""needed to reproduce this error"""
		printError( getresname.__module__+'.'+getresname.__name__, message, RuntimeError )
	
	#Including others..
	# FIXME: To be DEPRECATED
	for name, (resLatex,res) in sorted(adjectDict.iteritems(),reverse=True):
		if aFile.find( name ) != -1:
			resonanceLatex += resLatex
			resonance += res

	return resonance,resonanceLatex
