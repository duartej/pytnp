"""
Module with utilities for the pytnp class
"""
from management import printError, printWarning

def isVar( dataset, var ): 
	""".. function:: isVar( dataset, var ) -> bool

	Checks whether the variable ``var`` is in the RooDataSet or not
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param var: name of the variable to check
	:type var: string
	:return: True if the variable is within dataset
	:rtype: bool
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarDict( dataset )
	#---  All the binned variables in the dataset
	datasetVarList =  _swapDict.iterkeys()

	if var in datasetVarList:
		return True
	else:
		return False

def isbinnedVar( dataset, var, effName='efficiency', **keywords ):
	""".. function:: isbinnedVar( dataset, var, effName='efficiency'[, warning=bool] ) -> bool

	From a dataset checks if ``var`` is a binned variable.
	You can enter ``var`` as a list of variables, in this case checks for each 'var#' in the list.
	You can use 'warning=True' as argument to print a warning 
	in case do not find the variable.
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param var: variable(s) to be checked
	:type var: string or list of strings
	:param effName: name of the efficiency as found within the dataset. Default value: 'efficiency'
	:type effName: string
	:keyword warning: whether or not shows a warning message when a var is not found 
	:type warning: bool
	:return: True is variable(s) are binned variables of the dataset
	:rtype: bool
	"""
	#- Want warning?
	try:
		wantWarning = keywords['warning']
	except KeyError:
		wantWarning = False
	
	_swapDict = getVarDict( dataset )

	datasetVarList = filter( lambda x: x.lower().find(effName) == -1, _swapDict.iterkeys() )
	varList = []
	if isinstance(var,str):
		varList.append( var )
	elif isinstance( var, list ):
		varList = var

	isMissedAny = False
	message = ''
	for _variable in varList:
		if not _variable in datasetVarList:
			isMissedAny = True
			message +="""The RooDataSet '%s' does not contain '%s' as binned variable\n""" % (dataset.GetName(), _variable)
	message = message[:-1]

	if isMissedAny and wantWarning:
		printWarning( isbinnedVar.__module__+'.'+isbinnedVar.__name__, message )

	if isMissedAny:
		return False
	else:
		return True

def getVarNames( dataset, effName='efficiency' ):
	""".. function:: getVarNames( dataset, effName='efficiency' ) -> [ binnedvar1,...], effName

	From a dataset extract which binned variables have and returns
	the list of the variable's names and the efficiency name 
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name. Default value: 'efficiency'
	:type effName: string
	:return: 2-tuple composed by a list with the names of the binned variables and a string with the 
	         name of the efficiency
	:rtype: list of strings, string

	:raise AttributeError: not found the efficiency name introduced 
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarDict( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find(effName) == -1, _swapDict.iterkeys() )
	#--- Name of the efficiency
	effList = filter( lambda x: x.lower().find(effName) != -1, _swapDict.iterkeys() )
	#---- Sanity check: should have only one name 
	if len(effList) < 1:
		message ="""There is no efficiency variable called '%s'in the RooDataSet '%s'""" % (effName, dataset.GetName())
		printError( isbinnedVar.__module__+'.'+isbinnedVar.__name__, message, AttributeError )
	elif len(effList) > 1:
		message ="""It cannot be possible to parse the efficiency name, found '%s' in the RooDataSet '%s'\n""" % (str(effList), dataset.GetName())
		message +="""Check your root file and let only one variable to contain the name '%s'""" % effName
		printError( isbinnedVar.__module__+'.'+isbinnedVar.__name__, message, AttributeError )

	return datasetVarList, effList[0] 

def isEffNoNull( dataset, effName='efficiency' ):
	""".. function:: isEffNoNull( dataset, effName='efficiency' ) -> bool

	Given a dataset, the function evaluates if the variable
	effName has any value different from zero returning True,
	otherwise return False.
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name
	:type effName: string
	:return: True if the dataset contains at least one efficiency value different zero
	:rtype: bool

	:raise AttributeError: not found the effiency name introduced 
	"""
	#-- Checking efficiency is there
	isEff = isVar( dataset, effName )
	if not isEff:
		message ="""There is no efficiency variable called '%s'in the RooDataSet '%s'""" % (effName, dataset.GetName())
		printError( isEffNoNull.__module__+'.'+isEffNoNull.__name__, message, AttributeError )
	#_swapDict = getVarDict( dataset )
	#effList = filter( lambda x: x.lower().find(effName) != -1, _swapDict.iterkeys() )
	#if len(effList) < 1:
	#	message ="""There is no efficiency variable called '%s'in the RooDataSet '%s'""" % (effName, dataset.GetName())
	#	printError( isEffNoNull.__module__+'.'+isEffNoNull.__name__, message, AttributeError )
	#elif len(effList) > 1:
	#	message ="""It cannot be possible to parse the efficiency name, found '%s'in the RooDataSet '%s'\n""" % (str(effList), dataset.GetName())
	#	message +="""Check your root file and let only one variable to contain the name '%s'""" % effName
	#	printError( isEffNoNull.__module__+'.'+isEffNoNull.__name__, message, AttributeError )

	_table = tableEff( dataset, effName )
	# FIXME: Comparation between double and 0.0 -- better abs(var) < 1e-10, for example
	zeroList = filter( lambda (var,varLo,varHi): var == 0.0 and varLo == 0.0 and varHi == 0.0,  _table[effName] )
	
	if len(zeroList) == len(_table[effName]):
		return False
	else:
		return True


def getVarDict( dataset, __effName='efficiency' ):
	""".. function:: getVarDict( dataset, effName='efficiency' ) -> dict

	Given a RooDataSet, the function returns a dictionary whose keys are
	the binned variables and efficiency names and the values are a 
	dictionary with some useful info::

	  { 'var1': { 'latexName': 'blaba', 'unit': 'unit',
	              'binN': NumberBins, 'arrayBins' : (val1,...,valN+1)
	            },
		... 
          }
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name
	:type effName: string
	:return: see above
	:rtype: dict

	:raise TypeError: if the dataset is not a ROOT.RooDataSet
	:raise AttributeError: not found the effiency name introduced 
	"""
	import ROOT 

	varinfo = {}
	try:
		arg = dataset.get()
	except AttributeError:
		message = 'The object \'%s\' is not a RooDataSet' % str(dataset)
		printError( getVarDict.__module__+'.'+getVarDict.__name__, message, TypeError )
	#-- Get the list with the name of the variables
	varList = arg.contentsString().split(',')
	for name in varList:
		if isinstance(arg[name],ROOT.RooCategory):
			continue
		binN, arrayBinPointer = getBinning( arg[name] )
		# Some memory problems with the Double array--> to tuple
		arrayBin = tuple( [ arrayBinPointer[i] for i in xrange(binN+1) ] )
		varinfo[name] = { 'unit': arg[name].getUnit(), 'latexName': arg[name].getTitle().Data(), \
				'binN' : binN, 'arrayBins': arrayBin 
				} #Note: some TString instance--> normalizing to str with Data method
	try:
		effName = filter( lambda x: x.lower().find(__effName) != -1, [i for i in varinfo.iterkeys()] )[0]
	except IndexError:
		message = 'The RooDataSet \'%s\' does not have the \'%s\' variable as efficiency' % (dataset.GetName(), __effName)
		printError( getVarDict.__module__+'.'+getVarDict.__name__, message, AttributeError )

	varinfo[effName]['latexName'] = '#varepsilon'

	return varinfo


def getEffFromDict( dataset, input_effName='efficiency', **keywords):
	""".. function:: getEffFromDict(RooDataSet, effName, var1=value[,var2=value2, ...]) -> eff, effErrorLow, effErrorHigh, dict

	Giving a binned variables returns the efficiency which 
	corresponds to those values. If the introduced variables 
	are the exhausted set of the RooDataSet, the output
	will be a tuple of efficiency plus a None object (CASE 1).
	Otherwise if the input variables don't cover all the 
	RooDataSet binned variables, the output will be the 
	efficiency tuple plus a dictionary which the names 
	of the remaining variables and efficiency as keys and 
	the tuples of their values as dictionary values (CASE 2).
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name. Default value 'efficiency'
	:type effName: string
	:keyword var1: name of the value with its value
	:rtype var1: float
	:return: tuple with efficiency values and a dictionary (None)
	:rtype: float,float,float,dict

	:raise AttributeError: if the dataset do not contain ``var``
	:raise UserWarning: if do not introduce at least one variable as keyword
	"""
	#---  All the binned variables in the dataset
	datasetVarList, effName = getVarNames( dataset, input_effName )
	#--- Checking if vars are in, and storing them in a list
	nameVarValueList = []
	nameVarList = []
	for var,value in keywords.iteritems():
		if not isbinnedVar( dataset, var, effName ):
			message ="""The RooDataSet '%s' does not contain '%s' as binned variable""" % (dataset.GetName(), var)
			printError( getEff.__module__+'.'+getEff.__name__, message, AttributeError )
		nameVarValueList.append( (var,value) )
		nameVarList.append( var )
	#---- Sanity check
	if len(nameVarList) < 1:
		message ="""You must introduce at least one variable"""
		printError( getEffFromDict.__module__+'.'+getEffFromDict.__name__, message, UserWarning )
	
	#--- Binned variables which are not entered as arguments of this function
	noAskVar = filter( lambda x: x not in nameVarList, datasetVarList )
	#--- Has introduce the user all the binned variables?
	#--- If so, when find the efficiency value just return it
	#--- otherwise it must store all the efficiency values 
	#--- which corresponds to the same variable value (the other
	#--- binned variables will vary).
	isbinnedComplete = False
	dictReturn = None
	noAskStr = ''
	if len(noAskVar) == 0:
		isbinnedComplete = True
	else:
		dictReturn = { effName: [] }
		#-- Want to keep the values of the binned values don't ask by the user
		#-- in order to save them to the dictionary
		tupleNoAskStr = ''
		for var in noAskVar:
			dictReturn[var] = []
			noAskStr += ',_table[\''+var+'\']'
			
	_table = tableEff( dataset, effName )
	
	#-- Checking the position where there are matches
	indexDict = {}
	for var,value in nameVarValueList:
		_ind = 0 
		indexDict[var] = []
		for central,low,high in  _table[var]:
			if low <= value and high > value:
				indexDict[var].append( _ind )
			_ind += 1
	#-- Merging all the matches indexes
	indexList = indexDict.values()
	indexSet = set( indexList[0] )
	for i in xrange(len(indexList)-1):
		indexSet = indexSet.intersection( indexList[i+1] ) 

	_tableList = eval('zip(_table[effName]'+noAskStr+')')
	for i in filter( lambda _ind: _ind in indexSet, xrange(len(_tableList)) ):
		try:
			eff,theOthers = _tableList[i]
			#-- Note the behaviour of tuple: (a,b,c) != ((a,b,c),)
			if len(theOthers) == 3:
				theOthers = (theOthers,)
			dictReturn[effName].append( eff )
			_index = 0
			for name in noAskVar:
				#-- The order of variables are in noAskVar
				dictReturn[name].append( theOthers[_index] )
				_index += 1
		except ValueError:
			#-- Note: due to the zip, the output will be ((eff,effL,effH),)
			eff,effL,effH = _tableList[i][0]
			return eff, effL, effH, None
	
	if (len(dictReturn[effName])) > 0:
		return dictReturn
		

def getEff( dataSet, input_effName='efficiency', **keywords):
	""".. function:: getEff(dataset, effName='efficiency', var1=value[,var2=value2, ...]) -> eff, effErrorLow, effErrorHigh (,dict)

	Giving a binned variables returns the efficiency which 
	corresponds to those values. There is 2 output signatures 
	depending of the argument variables introduced; if the 
	variables are the exhausted set of the RooDataSet, the output
	will be a tuple of efficiency (CASE 1). Otherwise if the
	input variables don't cover all the RooDataSet binned 
	variables, the output will be the efficiency tuple plus
	a dictionary which the names of the resting variables as keys
	and the tuples of their bin values as values (CASE 2).
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param input_effName: efficiency name
	:type input_effName: string
	:keyword var: var=value
	:rtype var: object
	:return: tuple with efficiency values (and a dictionary)
	:rtype: float,float,float(,dict)
	
	:raise UserWarning: if do not introduce at least one variable as keyword
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarDict( dataSet )
	#---  All the binned variables in the dataset
	datasetVarList, effName = getVarNames( dataSet, input_effName )

	varList = []
	nameVarList = []
	for var,value in keywords.iteritems():
		if not isbinnedVar( dataSet, var, effName, warning=True ):
			raise KeyError
		varList.append( (var,value) )
		nameVarList.append( var )
	#---- Sanity check
	if len(nameVarList) < 1:
		message ="""You must introduce at least one variable"""
		printError( getEff.__module__+'.'+getEff.__name__, message, UserWarning )
	#--- Variables the user don't ask. This is the case when the user
	#--- wants a list of efficiency given a fixed value of one variable
	noAskVar = filter( lambda x: x not in nameVarList, datasetVarList )
	listReturn = False
	effVarList = None
	if len(noAskVar) != 0:
		listReturn = True
		effVarList = []
	#---- Sanity check
	if len( varList ) > len(datasetVarList):#FIXME---> can be more than 2 variables...
		message ="""You are using more variables than in dataset '%s'""" % dataSet.GetName()
		printError(getEff.__module__+'.'+getEff.__name__, message, AttributeError )

	#-- Get the table of efficiencies
	tableList = listTableEff( dataSet ) 

	for valDict in tableList:
		#--  From the list of the variables we want the efficiencies (varList), put the value inside  
		#--- of the ranges (valDict[var][1:][i]) in the list 
		fList = filter( lambda (var,value): valDict[var][1:][0] <= value and valDict[var][1:][1] > value , varList )
		#--  If our variables are all the variables available, we have 1-to-1 correspondence
		#--- with a efficiency value-> return this value
		if not listReturn and len(fList) == len( varList ):
			return valDict[effName]
		#--  If our variables are less than the variables available, we're going to return
		#--- a list with the (restOfvariables,efficiencies) in order to recover the 1-to-1 correspondence
		elif listReturn and len(fList) != 0:
			restVarDict = dict( [ (_name, valDict[_name]) for _name in noAskVar ] )
			effVarList.append( (valDict[effName],restVarDict) )

	if listReturn and len(effVarList) > 0 :
		#--output: (tuple,dict) where tuple is efficiency values and dict have the
		#--- names of the variables as keys and tuple as values  
		return effVarList

	message = '\033[1;34mpytnp.getEff Info: There is no bin where live '
	for var,val in varList:
		message += var+'='+str(val)+', '
	message = message[:-2]+'\033[1;m'
	print message

	# FIXME: Strange behaviour with version 3_6_1_patch4 (really with the RooFit (3.12 ??) included in this version:
	#        The values of the listTableEff do not fill correctly. All the dictionary is filled of the same value (the last found value)
	#        Still have this problem with RooFit 3.13, root-v5.27, python 2.6 ... 
	return None


def getBinning( var ):
	""".. function:: getBinning( var ) -> bins, arrayBins

	Giving a RooArgVar, the function returns 
	how many bins the variable has and an array (of doubles)
	with with his values.
	
	:param var: variable object
	:type var: ROOT.RooArgVar
	:return: number of bins and array with bin edges
	:rtype: int, double*

	.. warning::
	   Use with caution. The double arrays are potentially dangerous.
	"""

	binsN = var.numBins()
	binning = var.getBinning()
	arrayBins = binning.array()
	#-- By default arrayBins have a lot of space, so usign SetSize
	#---- to resize the array
	#---- The number of elements = bins+1 (remember edges)
	arrayBins.SetSize(binsN+1)

	return binsN, arrayBins

def graphclassname( tnp, dataname ):
	""".. function:: graphclassname( tnp, dataname ) -> name

	Giving a pytnp instance and a RooDataSet name contained in it, the
	function returns a string which defines the graph class that RooDataSet
	belongs. A graph class is defined by the keys ``effType``, ``objectType``
	and ``methodUsed``
	
	:param tnp: object instance of pytnp class
	:type tnp: pytnp
	:param dataname: name of the RooDataSet
	:type str: string
	:return name: name of the graph class
	:rtype: string

	:raise UserWarning: when the RooDataSet do not belong to the pyntp instance introduced
	"""
	#-- Check dataset
	try:
		return tnp[dataname]['effType']+'_'+tnp[dataname]['objectType']+'_'+tnp[dataname]['methodUsed']
	except KeyError:
		message = "The RooDataSet '%s' do not belong to the pyntp instance introduced" % dataname
		printError( graphclassname.__module__+'.'+graphclassname.__name__, message, UserWarning )


def newtableLatex( dataset, effName, varX, varY, **keyword ):
	""".. function tableLatex( dataset, effName, 'var_column', 'var_row', [outfile='name.tex', varXname='latex name', varYname='latex name'] ) -> dict

	Giving a RooDataSet and two variables, the function returns a table in latex
	format. If enters the keyword 'outfile' also the table will put
	it into the file.
	(The keyword var is a list with the name of the variables the user want to
	dump. TODO, not yet implemented)
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name
	:type effName: string
	:param varX: the name of the variable you want to be as column
	:rtype varX: string
	:param varY: the name of the variable you want to be as row

	.. seealso:: :func:`tableLatex`
	"""
	#TODO:	The keyword var is a list with the name of the variables the user want to dump.
	#TODO: CHECK IF WORKS CORRECTLY
	message = "Use this function with caution! Still in development.\n Use instead the tableLatex function"
	printWarning( newtableLatex, message )

	#---- Checking the variables in dataset
	varDict = getVarDict( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find(effName) == -1, varDict.iterkeys() )
	effList = filter( lambda x: x.lower().find(effName) != -1, varDict.iterkeys() )
	#---- Sanity check
	if len(effList) != 1:
		message ="""The RooDataSet '%s' does not contain a variable called '%s' as efficiency"""\
				% ( dataset.GetName(), effName )
		printError( tableLatex.__module__+'.'+tableLatex.__name__, message, AttributeError )
	#---- Variables are there?
	for var in [ varX, varY ]:
		if var not in datasetVarList:
			message ="""The RooDataSet '%s' does not contain a binned variable called '%s'"""\
					% ( dataset.GetName(), var )
			printError( tableLatex.__module__+'.'+tableLatex.__name__, message, AttributeError )
	# The table
	_tableDict = tableEff( dataset, effName )

	bins = {}
	varName = {}
	varUnit  = {}
	for var in [varX, varY]:
		#-- dictionary-List with the min and max values per bin (min,max),...
		bins[var] = [ ( varDict[var]['arrayBins'][i], varDict[var]['arrayBins'][i+1] ) \
				for i in xrange( len(varDict[var]['arrayBins'])-1) ]
		# Latex name of variables, maybe introduced by user otherwise take from construction
		try:
			# Remember to parse linux to latex \theta --> \\theta
			varName[var] = '$'+keywords[var].replace('\\','\\\\')+'$'
		except NameError:
			varName[var] = '$'+varDict[var]['latexName'].replace('\\','\\\\').replace('#','\\')+'$'
		varUnit[var] = varDict[var]['unit']
		if len(varUnit[var]) != 0:
			varUnit[var] = '$({\\rm '+varUnit[var]+'})$'

	#Some usefuls function to deal with latex
	edges = lambda x,y: '(%0.1f, %0.1f)' % (x,y) 
	effsetter = lambda eff,lo,hi: '$%.3f\\pm^{%.3f}_{%.3f}$ & ' % (eff,hi-eff,eff-lo) 
	central = lambda low,high: (high+low)/2.0

	#-- Table latex construction
	toLatex = '\\begin{tabular}{c'
	#-- Number of table columns
	toLatex += 'c'*varDict[varY]['binN']+'}\\hline\n'
	#-- Header (first line)
	toLatex += varName[varX]+varUnit[varX]+' {\\boldmath$\\backslash$}'+\
			varName[varY]+varUnit[varX]+' & '
	#-- varY bins are put on the first line
	for low, high in bins[varY]:
		toLatex += edges(low,high)+' & '
	toLatex = toLatex[:-2]+'\\\\ \\hline\n'
	#--- Finally, fill the table, line by line
	for lowX,highX in bins[varX]:
		toLatex += edges(lowX,highX)+' & '
		for lowY,highY in bins[varY]:
			try:
				eff,effErrorLow,effErrorHig = eval('getEff(dataset,effName,'+\
						varX+'=central(lowX,highX), '+varY+'=central(lowY,highY))')
				toLatex += effsetter(eff,effErrorLow,effErrorHig)
			#Empty bin
			except TypeError:
				toLatex += ' & '
		toLatex = toLatex[:-2]+'\\\\\n'
	toLatex += ' \\hline\n'
    	toLatex += '\\end{tabular}'
	
	print toLatex
	return toLatex



def tableLatex(dataset, inputEffName = 'efficiency'):
	"""
	tableLatex( dataset, inputEffName ) -> list

	Giving a RooDataSet, the function returns a table in latex format 
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param inputEffName: efficiency name
	:type inputEffName: string
	:return: string in latex format
	:rtype: string
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarDict( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find(inputEffName) == -1, _swapDict.iterkeys() )
	_swapeffList = filter( lambda x: x.lower().find(inputEffName) != -1, _swapDict.iterkeys() )
	#---- Sanity check
	if len(_swapeffList) != 1:
		message ="""ERROR: Unexpected Error!! It seems that in '%s' there is no"""\
				""" efficiency variable...""" % dataSet.GetName()
		printError( tableLatex.__module__+'.'+tableLatex.__name__, message, AttributeError )

	effName = _swapeffList[0]

	#Getting table
	effList = listTableEff(dataset)
	## Getting bins of variables
	#---- Dictionary with the bins for each binned variable
	binsTMP = map( lambda nameVar: { nameVar: set([ (i[nameVar][1],i[nameVar][2]) for i in effList ]) }, datasetVarList )
	bins =  {} #List from the map, only each item is a dict. Joining
	for Dict in binsTMP:
		for key,valDict in Dict.iteritems():
			bins[key] = valDict
	for key,SET in bins.iteritems():
		bins[key] = sorted(list(SET))
	#Assuming we have 2 binned variables:
	if len(bins) != 2:
		message = """\033[1;31mtableLatex Error: only two variables, by the moment\033[1;31m"""
		print message
	#FIXME
	etaBins = None
	for i,j in sorted(bins.iteritems()):
		etaBins = j
		etaName = i
		break
	ptBins = None
	KK = 0
	for i,j in sorted(bins.iteritems()):
		if KK == 1:
			ptBins = j
			ptName = i
			break
		KK += 1
	
	etaNbins = len(etaBins)
	ptNbins = len(ptBins)
	#Some usefuls function
	edges = lambda x,y: '(%0.1f, %0.1f)' % (x,y) 
	effsetter = lambda eff,lo,hi: '$%.3f\\pm^{%.3f}_{%.3f}$ & ' % (eff,hi-eff,eff-lo) 
	central = lambda low,high: (high+low)/2.0

	
	toLatex = '\\begin{tabular}{c'
	#Number of columns
	toLatex += 'c'*etaNbins+'}\\hline\n'
	#header
	toLatex += '$p_T^\\mu({\\rm GeV})$ {\\boldmath$\\backslash$}$\\eta^\\mu$  & '
	for low,high in etaBins:
		toLatex += edges(low,high)+' & '
	toLatex = toLatex[:-2]+'\\\\ \\hline\n'
	#Filling the table
	for lowPt,highPt in ptBins:
		toLatex += edges(lowPt,highPt)+' & '
		for lowEta,highEta in etaBins:
			try:
				eff,effErrorLow,effErrorHig = eval('getEff(dataset,inputEffName,'+\
						ptName+'=central(lowPt,highPt), '+etaName+'=central(lowEta,highEta))')
				toLatex += effsetter(eff,effErrorLow,effErrorHig)
			#Empty bin
			except TypeError:
				toLatex += ' & '
		toLatex = toLatex[:-2]+'\\\\\n'
	toLatex += ' \\hline\n'
    	toLatex += '\\end{tabular}'
#
	print toLatex
	return toLatex


def tableEff( dataset, effName = 'efficiency' ):
	"""
	tableEff( dataset, 'effName' ) --> tableDict

	Giving a RooDataSet, the function returns a dictionary where every 
	key is the 'variables' of the RooDataSet. Each value is a 
	list of tuples (var, varErrorLo, varErrorHigh):
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param effName: efficiency name
	:type effName: string
	:return: dict with efficiency values and binned variables
	:rtype: dict
	
	The output dictionary looks like::
		
		{ 
		  'efficiency': [ (eff1,effLo1,effHi1), (eff2,effLo2,effHi2), ... ],
		  'var_x'      : [ (varX1,xLo1,xHi1), (varX2,xLo2,xHi2), .... ],
		  'var_y'      : [ (varY1,yLo1,yHi1), (varY2,yLo2,yHi2), .... ],
		  ...
		}

	.. note:: There is another version to extract the table, see the function :func:`listTableEff`, a little more efficient than this one	
	"""
	#--- Getting variables from dataset, note that if dataset is not a RooDataSet,
	#--- getVarDict raise an AttributeError exception
	_swapDict = getVarDict( dataset )
	datasetVarList = [ i for i in _swapDict.iterkeys() ]
	#--- Is efficiency in dataset?
	if not effName in datasetVarList:
		message = 'Do not found \'%s\' as the name of the efficiency in the dataset \'%s\'' % (effName,dataSet.GetName())
		printError( tableEff.__module__+'.'+tableEff.__name__, message, KeyError )
	
	#--- Extract the RooArgSet (container of variables)
	argset = dataset.get()
	#--- Output table dictionary
	_table = dict( [ (var, []) for var in _swapDict.iterkeys() ] )
	#--- Looping all the 'events'
	for ev in xrange( dataset.numEntries() ):
		#--- event
		dataset.get(ev)
		for varName, valueList in _table.iteritems():
			variable = argset[varName]
			valueList.append( (variable.getVal(), variable.getVal()+variable.getErrorLo(), variable.getVal()+variable.getErrorHi()) )
	#-- In principle, I don't have to control errors: getVarDict is coherent with dataset.get, the same variables must
	#-- exist
	return _table



def listTableEff(dataSet,*badpoints,**effName):
	"""
	listTableEff( dataset ) --> tableList

	Giving a RooDataSet, the function returns a list where every 
	element is an entry of the RooDataSet stored as a dictionary:
	
	:param dataset: dataset
	:type dataset: ROOT.RooDataSet
	:param input_effName: efficiency name
	:type input_effName: string
	:return: list with efficiency values and binned variables
	:rtype: list

	The output list will be::
		
		[ 
		  { 'efficiency': (eff1,effLo1,effHi1),
		    'var_a'      : (a1,aLo1,aHi1), 
		    'var_b'      : (b1,b1,b1)
		  },
		  { 'efficiency': (eff2,effLo2,effHi2),
		    'var_a'      : (a2,aLo2,aHi2), 
		    'var_b'      : (b2,b2,b2)
		  },
		  ...
		]

	.. warning:: 
	   The description of this function must be revisited...
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarDict( dataSet )
	datasetVarList = [ i for i in _swapDict.iterkeys() ]
	#--- Bad points: TO BE DEPRECATED
	checkPoints = False
	for key,name in effName.itervalues():
		if len(badpoints) == 2:
			checkPoints = True
			effName = name
			#---- Check the efficiency name is in the dataset
			if not effName in datasetVarList:
				print '\033[1;31pytnp.listTableEff Error: % is not the name of the efficiency in the dataset %s\033[1;m' % (effName,dataSet.GetName())
				raise KeyError
	try:
		argSet = dataSet.get()
	except AttributeError:
		print '\033[1;31mpytnp.listTableEff Error: '+str(dataSet)+' is not a RooDataSet\n\033[1;m'
		raise AttributeError

	varDict = dict( [ ( varName, argSet[varName]) for varName in datasetVarList ] )
	valList= []
	for i in xrange(dataSet.numEntries()):
		dataSet.get(i)
		# Watch: for binned variables Hi and Lo is the limit of the bin
		#        for efficiencies are the upper and lower 
		valList.append( dict( [ (varName,(argset.getVal(), argset.getVal()+argset.getErrorLo(),\
				argset.getVal()+argset.getErrorHi()) ) for varName,argset in varDict.iteritems() ] ) )
		# Remove badpoints: TO BE DEPRECATED
		if checkPoints:
			isBad = filter( lambda (eff,lo,hi): (eff- badpoints[0]) < 1e-10 and ((eff-lo)-badpoints[1]) < 1e-10 , valList[-1][name] ) 
			if len(isBad) != 0:
				varList = varList[:-1]
	
	return valList


