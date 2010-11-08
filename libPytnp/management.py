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

def parserConfig( config_file, key ):
	"""
	"""
	import os.path
	import sys

	#-- Check the file is in the working directory
	if not os.path.isfile( config_file ):
		message = "File not exists: '%s'" % config_file
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, IOError )

	# FIXME: Potential errors with some python modules names
	#        maybe the file name must be a unique hardcoded name
	config_mod = config_file.replace('.py','')
	sys.path.append( '.' )
	try:
		config = __import__(config_mod)
	except ImportError:
		print "You have to put the configuration file '%s' in the working directory" % config_file
	#Dictionary of files --> (LatexName, name)
	try:
		value = eval('config.'+key)
	except AttributeError:
		message = "'%s' dictionary not found in the config file '%s'" % (key,config_file)
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, AttributeError )
	
	if key == 'DataNames':
		return parserDataNames(value)
	else:
		message = "Option '%s' not understood for the configuration" % key
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, AttributeError )


def parserDataNames(DataName):
	"""
	"""
	#-- Check the right format:
	isFormatRight = True
	namesDict = {}
	for fileName, value in DataName.iteritems():
		if not isinstance(value, tuple):
			message = "Erroneous format:\n\t\t"
			message += "%s: %s" % (fileName, str(value))
			printWarning( parserConfig.__module__+'.'+parserConfig.__name__, message )
			isFormatRight = False
		namesDict[fileName] = (value[0],value[1])
	
	if not isFormatRight:
		message = "Error parsing '%s'" % config_file
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, AttributeError )

	return namesDict
