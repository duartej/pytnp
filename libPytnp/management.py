"""
Generic functions for management use
"""

def printError( name, message, _exception ):
	""".. function:: printError(name, message, _exception) 

	Print a error message (in red color) and raise an exception

	:param name: module which call
	:type name: string
	:param message: message to print
	:type message: string
	:param _exception: exception to raise
	:type _exception: Exception
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess += '\033[1;31m'+name+' Error: '+l+'\n\033[1;m'
	print mess
	raise _exception

def printWarning( name, message ):
	""".. function:: printWarning(name, message) 

	Print a warning message (in yellow color) and continue

	:param name: module which call
	:type name: string
	:param message: message to print
	:type message: string
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess = '\033[1;33m'+name+' Warning: '+message+'\033[1;m\n'
	mess = mess[:-1]
	print mess
	
def parserConfig( config_file, key ):
	""".. function:: parserConfig( config_file, key ) -> dataset

	Parse the configuration file, after some checkings delegate
	to ``parserDataNames`` or ``parserAttributes`` functions

	:param config_file: name and route of the configuration file
	:type config_file: string
	:param key: name of the object you want to parse
	:type key: string

	:raise IOError: ``config_file`` not found
	:raise AttributeError: the key object has not exist in the configuration file
	:raise UserWarning: error parsing DataNames key
	:raise KeyError: the key object introduced is not implemented in this parser (DEPRECATED)

	.. warning::
	   To be deprecated the return dataset
	"""
	import os.path
	import sys

	#-- Check the file is in the working directory
	if not os.path.isfile( config_file ):
		message = "File not exists: '%s'" % config_file
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, IOError )

	# FIXME: Potential errors with some python modules names
	#        maybe the file name must be a unique hardcoded name?
	abspath = os.path.abspath( config_file )
	directory = os.path.dirname( abspath )
	config_name = os.path.basename( abspath )
	config_mod = config_name.replace('.py','')
	sys.path.append( directory )
	try:
		config = __import__(config_mod)
	except ImportError:
		# Have I raising exception?
		print "You have to put the configuration file '%s' in the working directory" % config_file
	# Attribute case: pytnpname::dataset
	keylist = key.split( '::' )
	key = keylist[0]
	try:
		dataname = keylist[1]
	except IndexError:
		pass
	#Dictionary of files --> (LatexName, name)
	try:
		value = eval('config.'+key)
	except AttributeError:
		message = "'%s' dictionary not found in the config file '%s'" % (key,config_file)
		printError( parserConfig.__module__+'.'+parserConfig.__name__, message, AttributeError )
	
	if key == 'DataNames':
		try:
			return parserDataNames(value)
		except AttributeError:
			message = "Error parsing '%s'" % config_file
			printError( parserConfig.__module__+'.'+parserConfig.__name__, message, UserWarning )
	else:
		return parserAttributes(value,dataname)
		#FIXME: WARNING, now left with no control any key unknown...

		#message = "Option '%s' not understood for the configuration" % key
		#printError( parserConfig.__module__+'.'+parserConfig.__name__, message, KeyError )


def parserDataNames(DataName):
	""".. function:: parserDataNames(DataNames) -> namesDict

	Parse the DataName dictionary of a configuration file

	:param DataName: dictionary 
	:type dictObject: dict

	:return: dictionary with ``pytnpname`` and latex names for each file
	:rtype: dict
	"""
	#-- Check the right format:
	isFormatRight = True
	namesDict = {}
	#--- Extract the values
	for fileName, value in DataName.iteritems():
		if not isinstance(value, tuple):
			message = "Erroneous format:\n\t\t"
			message += "%s: %s" % (fileName, str(value))
			printWarning( parserConfig.__module__+'.'+parserConfig.__name__, message )
			isFormatRight = False
		namesDict[fileName] = (value[0],value[1])
	
	if not isFormatRight:
		raise AttributeError

	return namesDict

def parserAttributes(dictObject, dataname):
	""".. function:: parserAttributes(attributes) -> attrDict

	Just checking the format attributes of a configuration file

	:param dictObject: pytnp dataset dictionary
	:type dictObject: dict
	:param dataname: name of the dataset
	:type key: string

	:return: tuple of values
	:rtype: (string,string,int)

	"""
	#-- Is there any key for this dataset?
	try:
		tupleAtt = dictObject[dataname]
	except KeyError:
		return None        
	#-- Check the right format:
	if not isinstance(tupleAtt, tuple) or len(tupleAtt) != 3:
		message = "Erroneous format: "
		message += "%s: %s" % (dataname, str(tupleAtt))
		printWarning( parserConfig.__module__+'.'+parserConfig.__name__, message )

	return tupleAtt
	
