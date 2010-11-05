"""
"""

def printError( name, message, _exception ):
	"""
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess += '\033[1;31m'+name+' Error: '+l+'\n\033[1;m'
	print mess
	raise _exception

def printWarning( name, message ):
	"""
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess = '\033[1;33m'+name+' Warning: '+message+'\033[1;m\n'
	mess = mess[:-1]
	print mess

