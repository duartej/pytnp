"""
Function utilities which uses the pytnp class to do several plots
"""

from pytnp.libPytnp.tnputils import  *
from pytnp.libPytnp.management import printError,printWarning

def superImposed( tnpDict, variable, Lumi, **keywords ):
	"""
	superImposed( { resName1: tnp1, resName2: tnp2,...} , 'variable', Lumi ) 
	
	Giving different pytnp instances, the function do the 1-dim plots of the 'variable'
	in the same canvas. The pytnp instances must have the same object types (objectType)
	(ex: Global muon identification efficiency, ...) with the SAME name.
	See the objectType content of a pytnp instance usign the print function for a
	pytnp instance. 

	.. warning::
	   
	   Queda al usuario preocuparse de tener los mismos bines entre datasets (bin0 en 
	   un dataset es el mismo bin0 en el otro)
	"""
	import ROOT
	import rootlogon
	from plotfunctions import legend, paveText, plotAsymGraphXY

	# Input keywords and defaults
	KEYWORDS = { 'title': None, 'outputformat': 'eps' }
	
	for key,value in keywords.iteritems():
		try:
			KEYWORDS[key] = value
		except KeyError:
			pass

	COLOR = [ 1, 38, 46, 28, 30 ] 
	MARKERTYPE = [ 20, 21, 22, 23, 24 ]
	#-- Checking we have the same efficiency object for each instance
	
	#-- Going to construct a string identifying totally all the 
	#-- RooDataSet which have the same effType, objectUse, methodUsed keys
	#-- plus variable and bin range information. This define a class
	#-- and each class it will be plotted at the same canvas
	# FIXME: QUE PASA CON MONTECARLO???!!!!! Ahora esta metido por defecto
	classesDict = {}
	for resName, tnp in tnpDict.iteritems():
		for dataname, keys in tnp.RooDataSet.iteritems():
			#-- Don't do the plots again if already done
			try:
				dummy = tnp[dataname]['tgraphs']
			except KeyError:
				#-- Plotting and storing
				tnp.plotEff1D( dataname, variable, Lumi )
			#-- Get the info for the tgraphs dict
			for className, graphDict in tnp[dataname]['tgraphs'].iteritems():
				for _graphname in graphDict.iterkeys():
					#-- Normalizing the graph names
					pseudoname = _graphname.replace( resName+'_'+className, '' )
					try:
						classesDict[className].add( pseudoname )
					except KeyError:
						classesDict[className] = set([ pseudoname ])
	#--- All it's done if we have only a file. FIXME: Quizas no, si nos interesa trabajar
	#---                                              con datasets del mismo fichero
	if len(tnpDict) == 1:
		return
	#--- Each key of the classes dict defines a canvas. 
	#--- Extracting all the graphs from all the datasets
	for className, graphpseudonameList in classesDict.iteritems():
		#-- FIXME: Queremos que el Montecarlo este activo? Queremos que un mismo rootfile
		#---       tenga la posibilidad de plotearse
		for pseudoname in graphpseudonameList:
			i = 0
			frame = None
			involvedRes = ''
			c = ROOT.TCanvas()
			leg = legend()
			if KEYWORDS['title']:
				text = paveText( KEYWORDS['title'] )
			for resName, tnp in tnpDict.iteritems():
				involvedRes += resName+'_'
				for dataname, dataDict in tnp.iteritems():
					try:
						#-- FIXME: Necesito algo para evitar que RooDataSets con el mismo patron
						#---       y en el mismo fichero se solapen. O quizas marcarlo
						#---       como construccion erronea de la instancia (effType, object...)
						#---       Seguro ??
						graph = dataDict['tgraphs'][className][resName+'_'+className+pseudoname]
					except KeyError:
						continue
					#-- Initializing the frame, cosmethics, ... once
					#--- FIXME: ONLY TAKE THE FIRST GRAPH AXIS!! Ok if every graph
					#----       have the same ranges but no in other case
					if not frame:
						refFrame = graph.GetHistogram()
						_ranges = { 'X' : None, 'Y': None }
						for axisName in _ranges.iterkeys():
							axis = eval( 'refFrame.Get'+axisName+'axis()' )
							Nbins = axis.GetNbins()
							_min = axis.GetBinLowEdge( 1 )
							_max = axis.GetBinUpEdge( Nbins )
							_ranges[axisName] = (_min,_max)
						frame = c.DrawFrame( _ranges['X'][0], _ranges['Y'][0], _ranges['X'][1], _ranges['Y'][1] )
						xtitle = dataDict['binnedVar'][variable]['latexName'] 
						unit = dataDict['binnedVar'][variable]['unit']
						if unit != '':
							xtitle += ' ('+unit+') '
						frame.GetXaxis().SetTitle( xtitle )
						frame.GetYaxis().SetTitle( tnp.effName )
						frame.Draw()

					graph.SetLineColor( COLOR[i] )
					graph.SetMarkerColor( COLOR[i] )
					graph.SetMarkerStyle( MARKERTYPE[i] )
					graph.Draw('PSAME')
					leg.AddEntry( graph, tnp.resLatex, 'P' )
					i += 1
					#	print resName+'_'+className+pseudoname
			leg.Draw()
			if KEYWORDS['title']:
				text.Draw()
			c.SaveAs(involvedRes+className+pseudoname+'.'+KEYWORDS['outputformat'])
			c.Close()
	
	#-- TO BE REMOVED: DEPRECATED
	#-- If there no plotted graph, the user possibly misunderstood the functionality of this function
	#if howPlottedGraphs == 0:
	#	print """ """
	#	print """\033[1;39mCAVEAT: No graph has been plotted! The correct use of this function implies\n\033"""\
	#			"""        that the root files involved contains the same object type efficiency.\n"""\
	#			"""        (See the contents of a pytnp instance, for example  effPlots -p -i rootfile.root)\n"""\
	#			"""        and look the 'objectType' key from the output\033[1;m"""
		# Raise a exception ??

def diff2DMaps( tnpRef, tnp2, varX, varY, Lumi, *nameOfdataSet ):
	"""
	diff2DMaps( pytnpRef, pytnpOther, nameOfdataSet, nameOfdataSet2 ) 

	Given 2 pytnp instances, it will do 2-dimensional maps::
	
	  |eff_ref-eff_other|sqrt(sigma_ref^2+sigma_other^2      Comparing_ResNameRef_ResNameOther_nameOfdataSet.eps     
          |eff_ref-eff_other|eff_ref                             ComparingRelative_ResNameRef_ResNameOther_nameOfdataSet.eps

	The two files must be have the same binning but one of them can have more bins. 
	The comparation will be done until the minimum of both
	"""
	from math import sqrt
	from plotfunctions import plotMapTH2F
	import rootlogon 
	#from pytnp.libPytnp.tnputils import isbinnedVar
	#from pytnp.libPytnp.tnputils import getBinning
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
		for i in [varX, varY]:
			if not isbinnedVar( dataSet, i ):
				message = "Variable '%s' is not a binned variable in the '%s' RooDataSet" % (i, nameOfdataSet)
				printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, UserWarning )
	except KeyError:
		print """\033[1;31mError: you must introduce a valid name\033[1;m"""
		raise KeyError
        try:
		dataSet2 = tnp2.RooDataSet[nameOfdataSet2]
		for i in [varX, varY]:
			if not isbinnedVar( dataSet2, i ):
				message = "Variable '%s' is not a binned variable in the '%s' RooDataSet" % (i, nameOfdataSet2)
				printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, UserWarning )
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
	#--- Checking binned variables  ##################################a
	datasetVarList, effName = getVarNames( dataSet )
	
	listTableEff1 = listTableEff( dataSet )

	xList = []
	yList = []
	effList = []
	for teff1 in listTableEff1:
		e1,e1lo,e1hi = teff1[effName]
		x,xlo,xhi = teff1[varX]
		y,ylo,yhi = teff1[varY]
		try:		
			e2,e2lo,e2hi = eval('getEff( dataSet2,'+varX+'='+str(x)+','+varY+'='+str(y)+')')
		except TypeError:
			#Not found efficiency in ptName-etaName  bin. Ignore that bin
			continue

		finalEffError = sqrt( ((e1hi-e1lo)/2.0)**2.0 + ((e2hi-e2lo)/2.0)**2.0 )   #Simetrizing errors
		#finalEff = abs(e1-e2)
		finalEff = e1-e2
		effList.append( (finalEff, finalEffError) )
		xList.append( x )
		yList.append( y )
	titles = {}
	for i in [varX,varY]:
		titles[i] = tnpRef[nameOfdataSet]['binnedVar'][i]['latexName']
		unit = tnpRef[nameOfdataSet]['binnedVar'][i]['unit'] 
		if unit != '':
			titles[i] += ' ('+unit+') '
	#k = 0
	XbinsN, arrayX = getBinning( dataSet.get()[varX] )
	YbinsN, arrayY = getBinning( dataSet.get()[varY] )
	for hist in histoList:
		ztitle = 'eff'
		title =' CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV ' 
		histoname = hist['plotName']
		hist['histo'] = plotMapTH2F( xList, yList, effList, titles[varX], titles[varY], ztitle, XbinsN, arrayX, YbinsN, arrayY, \
				title=title, graphname=histoname, rangeFrame = (0.0, 1.0) )


def diffEffMaps( tnpDict, refRes, varX, varY, Lumi, **keywords ):
	"""
	diffEffMaps( pytnp1, pytnp2, 'reference_resonance', 'Luminosity' )

	Plot 2-dim maps where each bin is calculated from the substraction
	of one efficiency values with respect the other (refRes has the 
	rol of first operand in the substraction)
	"""
	#Extract the reference resonance:
	try:
		tnpResRef = tnpDict.pop( refRes )
		# List of tuples (res,resLatex) from
		# the other but the reference
		resonance = []
		for tnp in tnpDict.itervalues():
			resonance.append( (tnp.resonance, tnp.resLatex) )
		
	except KeyError:
		message ="""
\033[1;31mError: the resonance name '%s' introduced is wrong, use either of '%s' \033[1;m""" % (refRes, [i for i in tnpDict.iterkeys()]) 
		print message
		raise KeyError
	#resonanceRef = resonance.pop( refRes )
	for resName,resLatex in sorted(resonance):
		for name in tnpDict[resName].RooDataSet.iterkeys():
			#FIXME ---_> No funcionara, signatura cambiado (necsita variables de entrada
			diff2DMaps( tnpResRef, tnpDict[resName], varX, varY, Lumi, name )



def sysMCFIT(tnp, Lumi, **keywords):
        """
	sysMCFIT( 'namerootfile' ) 

	Compute the differences between MC True counting efficiency
	and Tag and Probe fitted efficiency. Return plots (and 
	(TODO) root file) containing maps of the absolute differencies
        """
	import ROOT
	import rootlogon
	ROOT.gROOT.SetBatch(1)

	#TODO: Permitir que se puedan entrar dos ficheros
	#      Ahora mc debe estar en el mismo fichero
	#tnp = pytnp.pytnp(_file)

	effList = tnp.getFitEffList()
	
	pairFitMC = [ (tnp.getCountMCName(i),i) for i in effList ]
	##- Checking if there are MC true info
	for i in filter( lambda (mc,fitEff): not mc, pairFitMC ):
		message = """The '%s' does not contains MC True information""" % tnp.__fileroot__.GetName()
		printError( sysMCFIT.__module__+'.'+sysMCFIT.__name__, message, AttributeError )

	for tMC, tFit in pairFitMC:
		diff2DMaps( tnp, tnp, Lumi, tMC, tFit )

