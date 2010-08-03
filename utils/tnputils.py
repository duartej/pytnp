
"""
Module with utilities
TODO: Descriptiona

	checkbinnedVar
	getVarInfo
	getEff
	getBinning
	tableLatex
	tableEff
"""
import ROOT

def checkbinnedVar( dataset ):
	"""
	checkbinnedVar( RooDataSet ) -> [ 'binnedvar1',...], 'effName' 

	From a dataset extract which binned variables have and returns
	the list of the variable's names and the efficiency name 
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataset )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find('eff') == -1, _swapDict.iterkeys() )
	#--- Name of the efficiency
	effList = filter( lambda x: x.lower().find('eff') != -1, _swapDict.iterkeys() )
	#---- Sanity check: should have only one name 
	if len(effList) != 1:
		message ="""\033[1;31mpytnp.tnputils.checkbinnedVar ERROR: Unexpected Error!! It seems that in %s there is no
efficiency variable...\033[1;m""" % dataSet.GetName()
		print message
		raise 

	return datasetVarList, effList[0] 



def getVarInfo( dataset ):
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
		raise KeyError
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
		effName = filter( lambda x: x.lower().find('eff') != -1, [i for i in varinfo.iterkeys()] )[0]
	except IndexError:
		print """#TODO: CONTROL DE ERRORES!!!"""
	varinfo[effName]['latexName'] = '#varepsilon'

	return varinfo

def getEff( dataSet, **keywords):
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
	datasetVarList = filter( lambda x: x.lower().find('eff') == -1, _swapDict.iterkeys() )
	effList = filter( lambda x: x.lower().find('eff') != -1, _swapDict.iterkeys() )
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
	tableList = tableEff( dataSet ) 

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
	#        The values of the tableEff do not fill correctly. All the dictionary is filled of the same value (the last found value)
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
	effList = tableEff(dataset)
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


def tableEff(dataSet,*badpoints,**effName):
	"""
	tableEff( dataSet ) --> tableList

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
				print '\033[1;31pytnp.tableEff Error: % is not the name of the efficiency in the dataset %s\033[1;m' % (effName,dataSet.GetName())
				raise KeyError
	try:
		argSet = dataSet.get()
	except AttributeError:
		print '\033[1;31mpytnp.tableEff Error: '+str(dataSet)+' is not a RooDataSet\n\033[1;m'
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

def getDiff2DPlots( tnpRef, tnp2, Lumi, *nameOfdataSet ):
	"""
	getDiff2DPlots( pytnpRef, pytnpOther, nameOfdataSet, nameOfdataSet2 ) --> 

	Given 2 pytnp instances, it will do 2-dimensional maps:

	|eff_ref-eff_other|sqrt(sigma_ref^2+sigma_other^2      Comparing_ResNameRef_ResNameOther_nameOfdataSet.eps     
        |eff_ref-eff_other|eff_ref                             ComparingRelative_ResNameRef_ResNameOther_nameOfdataSet.eps

	The two files must be have the same binning but one of them can have more bins. 
	The comparation will be done until the minimum of both
	"""
	from math import sqrt
	#---- Initialiting -------------------------------
	nameOfdataSet2 = None
	#-- Comparation between different resonances
	if len(nameOfdataSet) == 1:
		nameOfdataSet  = nameOfdataSet[0]
		nameOfdataSet2 = nameOfdataSet
		tnpRef_resLatex = tnpRef.resLatex
		tnp2_resLatex =  tnp2.resLatex
	#--- MC comparation
	elif len(nameOfdataSet) == 2: 
		nameOfdataSet2 = nameOfdataSet[1]
		nameOfdataSet  = nameOfdataSet[0] 
		tnpRef_resLatex = tnpRef.resLatex+'^{MC}'
		tnp2_resLatex = tnpRef.resLatex+'^{TnP}'
	else:
		message = """\033[1;31mUnexpected Error!!\033[1;m"""
		print message
		exit(-1)
        try:
		dataSet = tnpRef.RooDataSet[nameOfdataSet]
	except KeyError:
		print """\033[1;31mError: you must introduce a valid name\033[1;m"""
		raise KeyError
        try:
		dataSet2 = tnp2.RooDataSet[nameOfdataSet2]
	except KeyError:
		print """\033[1;31mError: you must introduce a valid name\033[1;m"""
		raise KeyError
	#---------------------------------------------------
	#--- Name for the histo and for the plot file to be saved
	plotName = 'Comparing_'+tnpRef.resonance+'_'+tnp2.resonance+'_'+nameOfdataSet.replace('/','_')
	#--- Title for the plot file
	title = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}| '+tnpRef[nameOfdataSet]['objectType']+' '+dataSet.GetTitle()
	plotName2 = 'ComparingRelative_'+tnpRef.resonance+'_'+tnp2.resonance+'_'+nameOfdataSet.replace('/','_')
	#--- Title for the plot file
	title2 = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#varepsilon_{'+tnpRef_resLatex+'}'+\
                          ' '+tnpRef[nameOfdataSet]['objectType']+' '+dataSet.GetTitle()
	# Dictionary of objects
	histoList = [ { 'histo': None, 'plotName': plotName, 'title': title},
			{ 'histo': None,  'plotName': plotName2, 'title': title2 } 
			]
	#--- Getting the binning and some checks: ##################################a
	datasetVarList, effName = checkbinnedVar( dataSet )
	#--- Harcoded for 2 variables
	if len(datasetVarList) != 2:
		message = """\033[1;31mPROVISONAL ERROR: must be 2 binned variables in dataset %s""" % dataSet.GetName()
		print message
		raise KeyError
	#---- The pt in the x-axis
	try:
		ptIndex = datasetVarList.index('pt')
	except ValueError:
		ptIndex = 0
	ptName = datasetVarList[ptIndex]
	etaName = datasetVarList[1-ptIndex] # -- datsetVarList have 2 elements

	argSet = dataSet.get()
	PT = argSet[ptName];
	ETA = argSet[etaName];
	ptNbins, arrayBinsPt = getBinning( PT )
	etaNbins, arrayBinsEta = getBinning( ETA )
	k = 0
	for thisHisto in histoList:
		hTitleOfHist = 'h'+nameOfdataSet.replace('/','_')+str(k)
		thisHisto['histo'] = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
		#thisHisto['histo'].SetTitle( thisHisto['title'] ) --> Out titles
		thisHisto['histo'].SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
		#thisHisto['histo'].SetTitle( '' ) 
		thisHisto['histo'].GetZaxis().SetLimits(0,1.0) # (6.5 Por que??)
		thisHisto['histo'].SetContour(50) # Aumenta el granulado de los colores
		thisHisto['histo'].GetZaxis().SetLabelSize(0.02)
		k += 1
	
	tableEff1 = tableEff( dataSet )
	for teff1 in tableEff1:
		e1,e1lo,e1hi = teff1[effName]
		pt,ptlo,pthi = teff1[ptName]
		eta,etalo,etahi = teff1[etaName]
		try:		
			e2,e2lo,e2hi = eval('getEff( dataSet2,'+ptName+'='+str(pt)+','+etaName+'='+str(eta)+')')
		except TypeError:
			#Not found efficiency in ptName-etaName  bin. Ignore that bin
			continue

		finalEffError = sqrt( ((e1hi-e1lo)/2.0)**2.0 + ((e2hi-e2lo)/2.0)**2.0 )   #Simetrizing errors
		#finalEff = abs(e1-e2)
		finalEff = e1-e2
		k = 0
		for hist in histoList:
			b = hist['histo'].FindBin( eta, pt )
			if k == 0:
				hist['histo'].SetBinContent( b, finalEff )    
				hist['histo'].SetBinError(b, finalEffError )
			elif k == 1:
				try:
					hist['histo'].SetBinContent( b, finalEff/e1 )    #WARNING
				except ZeroDivisionError:
					hist['histo'].SetBinContent( b, 0.0 )    

			k += 1
	k = 0
	for hist in histoList:
		c = ROOT.TCanvas()
		hist['histo'].GetYaxis().SetTitle('p_{t} (GeV/c)')
		hist['histo'].GetXaxis().SetTitle('#eta')
		hist['histo'].GetZaxis().SetTitle('eff')
		#hist['histo'].SetTitle( hist['title'] ) --> Out titlee
		#hist['histo'].SetTitle( '' )
		hist['histo'].SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
		hist['histo'].Draw('COLZ')
		#--- Only if is sigma plot
		if k >= 0: ###--- FIXME: De momento dejo que esten los valores
			htext = hist['histo'].Clone('htext')
			htext.SetMarkerSize(1.0)
			htext.SetMarkerColor(1)
			ROOT.gStyle.SetPaintTextFormat("1.3f")
			if ptNbins+etaNbins < 7:
				htext.SetMarkerSize(2.2)
			elif ptNbins+etaNbins > 14:
				htext.SetMarkerSize(0.7)
			htext.Draw('SAMETEXTE0')
		toPlotName = hist['plotName']+'.eps'
		c.SaveAs(toPlotName)
		c.Close()
		k += 1

