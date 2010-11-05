
"""
Module with utilities
TODO: Descriptiona

	checkbinnedVar
	getVarInfo
	getEff
	getBinning
	tableLatex
	listTableEff
"""
import ROOT
from management import printError, printWarning

def checkbinnedVar( dataset, effName='efficiency' ):
	"""
	checkbinnedVar( RooDataSet ) -> [ 'binnedvar1',...], 'effName' 

	From a dataset extract which binned variables have and returns
	the list of the variable's names and the efficiency name 
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find(effName) == -1, _swapDict.iterkeys() )
	#--- Name of the efficiency
	effList = filter( lambda x: x.lower().find(effName) != -1, _swapDict.iterkeys() )
	#---- Sanity check: should have only one name 
	if len(effList) < 1:
		message ="""There is no efficiency variable called '%s'in the RooDataSet '%s'""" % (effName, dataset.GetName())
		printError( checkbinnedVar.__module__+'.'+checkbinnedVar.__name__, message, AttributeError )
	elif len(effList) > 1:
		message ="""It cannot be possible to parse the efficiency name, found '%s'in the RooDataSet '%s'\n""" % (str(effList), dataset.GetName())
		message +="""Check your root file and let only one variable to contain the name '%s'""" % effName
		printError( checkbinnedVar.__module__+'.'+checkbinnedVar.__name__, message, AttributeError )

	return datasetVarList, effList[0] 

def isEffNoNull( dataset, effName='efficiency' ):
	"""
	isEffNoNull( RooDataSet, 'effName' ) --> bool

	Given a dataset, the function evaluates if the variable
	effName has any value different from zero returning True,
	otherwise return False.
	"""
	#-- Checking efficiency is there
	_swapDict = getVarInfo( dataset )
	effList = filter( lambda x: x.lower().find(effName) != -1, _swapDict.iterkeys() )
	if len(effList) < 1:
		message ="""There is no efficiency variable called '%s'in the RooDataSet '%s'""" % (effName, dataset.GetName())
		printError( isEffNoNull.__module__+'.'+isEffNoNull.__name__, message, AttributeError )
	elif len(effList) > 1:
		message ="""It cannot be possible to parse the efficiency name, found '%s'in the RooDataSet '%s'\n""" % (str(effList), dataset.GetName())
		message +="""Check your root file and let only one variable to contain the name '%s'""" % effName
		printError( isEffNoNull.__module__+'.'+isEffNoNull.__name__, message, AttributeError )

	_table = tableEff( dataset, effName )
	# FIXME: Comparation between double and 0.0 -- better abs(var) < 1e-10, for exemple
	zeroList = filter( lambda (var,varLo,varHi): var == 0.0 and varLo == 0.0 and varHi == 0.0,  _table[effName] )
	
	if len(zeroList) == len(_table[effName]):
		return False
	else:
		return True


def getVarInfo( dataset, __effName='efficiency' ):
	"""
	getDataSetVar( RooDataSet ) -> { 'var1': { 'latexName': 'blaba', 'unit': 'unit',
						    'binN': NumberBins, 'arrayBins' : (val1,...,valN+1)
						    },
					 ... 
				       }

	Given a RooDataSet, the function returns a dictionary whose keys are
	the binned variables and efficiency names and the values another 
	dictionary with some useful info (see above).
	"""
	varinfo = {}
	try:
		arg = dataset.get()
	except AttributeError:
		message = '\033[1;31mgetVarInfo: The object %s is not a RooDataSet\033[1;m' % str(dataset)
		print message
		raise AttributeError
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
		print """#TODO: CONTROL DE ERRORES!!!"""
	varinfo[effName]['latexName'] = '#varepsilon'

	return varinfo

def getEff( dataSet, input_effName, **keywords):
	"""
	getEff(RooDataSet, var1=value, ...) --> eff, effErrorLow, effErrorHigh                
	                                    --> eff, effErrorLow, effErrorHigh, dictionary

	Giving a binned variables returns the efficiency which 
	corresponds to those values. There is 2 output signatures 
	depending of the argument variables introduced; if the 
	variables are the exhausted set of the RooDataSet, the output
	will be a tuple of efficiency (CASE 1). Otherwise if the
	input variables don't cover all the RooDataSet binned 
	variables, the output will be the efficiency tuple plus
	a dictionary which the names of the resting variables as keys
	and the tuples of their bin values as values (CASE 2).
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataSet )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find(input_effName) == -1, _swapDict.iterkeys() )
	effList = filter( lambda x: x.lower().find(input_effName) != -1, _swapDict.iterkeys() )
	#---- Sanity check
	if len(effList) != 1:
		message ="""\033[1;31mpytnp.tnputils.getEff ERROR: Unexpected Error!! It seems that in %s there is no
efficiency variable...\033[1;m""" % dataSet.GetName()
		print message
		raise 
	effName = effList[0]

	varList = []
	nameVarList = []
	for var,value in keywords.iteritems():
		if not var in datasetVarList:
			message ="""\033[1;31mpytnp.tnputils.getEff ERROR: %s is not a binned variable of the dataset %s\033[1;m""" % (var,dataSet.GetName())
			print message
			raise KeyError
		varList.append( (var,value) )
		nameVarList.append( var )
	#---- Sanity check
	if len(varList) < 1:
		message ="""\033[1;31mpytnp.tnputils.getEff ERROR: You must introduce at least one variable\033[1;m"""
		print message
		print 'Usage:\n',getEff.__doc__
		raise 
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
		message ="""\033[1;31mpytnp.tnputils.getEff ERROR: You are using more variables than in dataset %s\033[1;m""" % dataSet.GetName()
		print message
		raise

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
	return None

def getBinning( var ):
	"""
	getBinning( ROOT.RooArgVar ) -> bins, arrayBins

	Giving a RooArgVar, the function returns 
	how many bins the variable has and an array (of doubles)
	with with his values.

	WARNING: Use with caution. The doubles array are
	         potentially dangerous.
	"""

	binsN = var.numBins()
	binning = var.getBinning()
	arrayBins = binning.array()
	#-- By default arrayBins have a lot of space, so usign SetSize
	#---- to resize the array
	#---- The number of elements = bins+1 (remember edges)
	arrayBins.SetSize(binsN+1)

	return binsN, arrayBins

def tableLatex(dataset):
	"""

	Giving a RooDataSet, the function returns a table in latex
	format 
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find('eff') == -1, _swapDict.iterkeys() )
	_swapeffList = filter( lambda x: x.lower().find('eff') != -1, _swapDict.iterkeys() )
	#---- Sanity check
	if len(_swapeffList) != 1:
		message ="""\033[1;31mpytnp.getEff ERROR: Unexpected Error!! It seems that in %s there is no
efficiency variable...\033[1;m""" % dataSet.GetName()
		print message
		raise 
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
#	Nbins = map( lambda i: len(i), bins )
#	##Getting how many eta and pt bins we have
#	etaBins = set([ (i['eta'][1],i['eta'][2]) for i in effList] )
#	etaBins = sorted(list(etaBins))
	etaNbins = len(etaBins)
#	ptBins  = set([ (i['pt'][1],i['pt'][2]) for i in effList] )
#	ptBins  = sorted(list(ptBins)) 
	ptNbins = len(ptBins)
	#Some usefuls function
	edges = lambda x,y: '(%0.1f, %0.1f)' % (x,y) 
	effsetter = lambda eff,lo,hi: '$%.3f\\pm^{%.3f}_{%.3f}$ & ' % (eff,hi-eff,eff-lo) 
	central = lambda low,high: (high+low)/2.0

	
	toLatex = '\\begin{tabular}{c'
	#Number of columns
	toLatex += 'c'*etaNbins+'}\\toprule\n'
	#header
	toLatex += '$p_T^\\mu({\\rm GeV})$ {\\boldmath$\\backslash$}$\\eta^\\mu$  & '
	for low,high in etaBins:
		toLatex += edges(low,high)+' & '
	toLatex = toLatex[:-2]+'\\\\ \\midrule\n'
	#Filling the table
	for lowPt,highPt in ptBins:
		toLatex += edges(lowPt,highPt)+' & '
		for lowEta,highEta in etaBins:
			try:
				eff,effErrorLow,effErrorHig = eval('getEff(dataset,'+ptName+'=central(lowPt,highPt), '+etaName+'=central(lowEta,highEta))')
			#Empty bin
			except TypeError:
				toLatex += ' & '
			toLatex += effsetter(eff,effErrorLow,effErrorHig)
		toLatex = toLatex[:-2]+'\\\\\n'
	toLatex += ' \\bottomrule\n'
    	toLatex += '\\end{tabular}'
#
	print toLatex
	return toLatex


def tableEff( dataset, effName ):
	"""
	tableEff( RooDataSet, 'effName' ) --> tableDict

	Giving a RooDataSet, the function returns a dictionary where every 
	key is the 'variables' of the RooDataSet. Each value is a 
	list of tuples (var, varErrorLo, varErrorHigh)
	"""
	#--- Getting variables from dataset, note that if dataset is not a RooDataSet,
	#--- getVarInfo raise an AttributeError exception
	_swapDict = getVarInfo( dataset )
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
	#-- In principle, I don't have tto control errors: getVarInfo is coherent with dataset.get, the same variables must
	#-- exist
	return _table



def listTableEff(dataSet,*badpoints,**effName):
	"""
	listTableEff( dataSet ) --> tableList

	Giving a RooDataSet, the function returns a list where every 
	element is an entry of the RooDataSet stored as a dictionary:
	For every entry we have
	                { 'var1':  (pt, minimum pt bin, maximum pt bin),
	                  'var2': (eta, minimum eta bin, maximum eta bin),
			   ...
			  'nameEfficiency': (eff, eff low, eff high)
			}
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataSet )
	datasetVarList = [ i for i in _swapDict.iterkeys() ]
	#--- Bad points
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
		# Remove badpoints
		if checkPoints:
			isBad = filter( lambda (eff,lo,hi): (eff- badpoints[0]) < 1e-10 and ((eff-lo)-badpoints[1]) < 1e-10 , valList[-1][name] ) 
			if len(isBad) != 0:
				varList = varList[:-1]
	
	return valList


