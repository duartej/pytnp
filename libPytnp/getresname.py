"""
"""

def getResName( aFile ):
	"""
	getResName( fileName ) -> str,str (latex)

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
			message ="""\033[1;33mgetResName: 
		WARNING: This function is highly dependent of the 
		name of the file, you need an standard format like:
		NameOFResonance_X_blabla.root

		Unrecognized name: \033[1;m\033[1;31m  %s\033[1;m""" % aFile
			print message
			return None
		
	except:
		message ="""\033[1;31mgetResName: 
		ERROR: Something wrong!! Check the code pytnp.utils.getResName
		because this is an unexpected error\033[1;m"""
		print message
		exit(-1)
	
	#Including others..
	for name, (resLatex,res) in sorted(adjectDict.iteritems(),reverse=True):
		if aFile.find( name ) != -1:
			resonanceLatex += resLatex
			resonance += res

	return resonance,resonanceLatex
