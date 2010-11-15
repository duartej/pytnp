"""
Function utilities which uses the pytnp class to do several plots
"""
#TODO: join superImposed and mcimposed in the same function
#      (similar way as it's done with diff2DMaps)

from pytnp.libPytnp.tnputils import  *
from pytnp.libPytnp.management import printError,printWarning

def superImposed( tnpDict, variable, Lumi, **keywords ):
	""".. function:: superImposed( tnpdict, variable, Lumi[, title=thetitle, outputformat=format] )
	
	Giving different pytnp instances, the function do the 1-dim plots of the 'variable'
	in the same canvas. The pytnp instances must have the same object types (objectType)
	(ex: Global muon identification efficiency, ...) with the SAME name.
	See the objectType content of a pytnp instance usign the print function for a
	pytnp instance. 

	:param tnpdict: { resName1: tnp1, resName2: tnp2,...}, the keys are strings and the values
	                pytnp instances 
	:type tnpdict: dict
	:param variable: the binned variable to be plotted
	:type variable: string
	:param Lumi: the luminosity to be put in the title (TO BE DEPRECATED)
	:type Lumi: string
	:keyword title: the title of the graph
	:type title: string
	:keyword outputformat: the output format of the graph (eps, root, png,...)
	:type outputformat: string

	.. warning::	   
	   The user is responsable of having the same binning in every dataset.

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
	#--- All it's done if we have only a file.
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

def mcimposed( tnp, variable, Lumi, sys='cnt', **keywords ):
	""".. function:: mcimposed( tnp, variable, sys[, title=thetitle, outputformat=format] )
	
	Function to do the 1-dim plots of the ``variable`` for all datasets which 
	attribute ``isMC=0`` with its correspondent Monte Carlo partner ``isMC=1``
	
	:param tnp: the pytnp instance
	:type tnpdict: pytnp
	:param variable: the binned variable to be plotted
	:type variable: string
	:param Lumi: the luminosity to be put in the title (TO BE DEPRECATED)
	:type Lumi: string
	:param sys: the efficiency type to be compared, ``fit`` or ``cnt``
	:type sys: string
	:keyword title: the title of the graph
	:type title: string
	:keyword outputformat: the output format of the graph (eps, root, png,...)
	:type outputformat: string
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

	COLOR = [ 1, 38, 46 ] 
	MARKERTYPE = [ 20, 21, 22 ]
	
	mcpartner = {}
	todelete = []
	for dataname, tnpdict in tnp.iteritems():
		isnotMC = False
		mcpartner[dataname] = []
		#-- Find the names for mc partners
		try:
			dummy = tnpdict['refMC']
			isnotMC = True
		except KeyError:
			pass
		#-- Do the plot if it still is not done
		try:
			dummy = tnp[dataname]['tgraphs']
		except KeyError:
			#-- Plotting and storing
			tnp.plotEff1D( dataname, variable, Lumi )
		
		if isnotMC:
			try:
				mcpartner[dataname].append( tnpdict['refMC'][sys+'_eff'] )
			except KeyError:
				Message = "No '%s' Monte Carlo dataset for '%s'. Skipping the plot..." % ( sys+'_eff', dataname )
				printWarning( mcimposed.__module__+'.'+mcimposed.__name__, Message )

	#-- Print in the same canvas every mc and data
	for dataname, tnpdict in filter( lambda (name, _dict): _dict['isMC'] == 0, tnp.iteritems() ):
		#-- Only plot those who find MC partner
		if len(mcpartner[dataname]) == 0:
			continue
		for className, graphDict in tnpdict['tgraphs'].iteritems():
			#-- Name of the class for the mc 
			mcclassName = className.replace( tnp[dataname]['methodUsed'], sys+'_eff' )
			if KEYWORDS['title']:
				text = paveText( KEYWORDS['title'] )
			for _graphname, graph in graphDict.iteritems():
				i = 0
				c = ROOT.TCanvas()
				#-- Initializing the frame, cosmethics, ...
				#--- FIXME: ONLY TAKE THE FIRST GRAPH AXIS!! Ok if every graph
				#----       have the same ranges but no in other case
				refFrame = graph.GetHistogram()
				_ranges = { 'X' : None, 'Y': None }
				for axisName in _ranges.iterkeys():
					axis = eval( 'refFrame.Get'+axisName+'axis()' )
					Nbins = axis.GetNbins()
					_min = axis.GetBinLowEdge( 1 )
					_max = axis.GetBinUpEdge( Nbins )
					_ranges[axisName] = (_min,_max)
				frame = c.DrawFrame( _ranges['X'][0], _ranges['Y'][0], _ranges['X'][1], _ranges['Y'][1] )
				xtitle = tnpdict['binnedVar'][variable]['latexName'] 
				unit = tnpdict['binnedVar'][variable]['unit']
				if unit != '':
					xtitle += ' ('+unit+') '
				frame.GetXaxis().SetTitle( xtitle )
				frame.GetYaxis().SetTitle( tnp.effName )
				frame.Draw()
				
				leg = legend()

				graph.SetLineColor( COLOR[i] )
				graph.SetMarkerColor( COLOR[i] )
				graph.SetMarkerStyle( MARKERTYPE[i] )
				graph.Draw('PSAME')
				leg.AddEntry( graph, tnp.resLatex, 'P' )
				i += 1
				#-- Name of the graph for the mc
				_graphmcname =  _graphname.replace( tnp[dataname]['methodUsed'], sys+'_eff' )+'__mcTrue'
				#-- Finding all the mc graphs in the list of partners
				for mcdataname in mcpartner[dataname]:
					try:
						graphmc = tnp[mcdataname]['tgraphs'][mcclassName][_graphmcname]
						graphmc.SetLineColor( COLOR[i] )
						graphmc.SetMarkerColor( COLOR[i] )
						graphmc.SetMarkerStyle( MARKERTYPE[i] )
						graphmc.Draw('PSAME')
						leg.AddEntry( graphmc, tnp.resLatex+' MC '+sys, 'P' )
						i += 1
					except KeyError:
						continue
				leg.Draw()
				if KEYWORDS['title']:
					text.Draw()
				c.SaveAs(_graphname+'_SYSMC''.'+KEYWORDS['outputformat'])	
				c.Close()


def diff2DMaps( refT, otherT, varX, varY, Lumi, **keywords ):
	""".. function:: diff2DMaps( tnpRef, tnpOther, varX, varY, Lumi\[,title=thetitle, outputformat=format] ) 

	Differences maps from 2 datasets::
	
	  eff_ref-eff_other                   Comparing
          |eff_ref-eff_other|/eff_ref         ComparingRelative --> DEPRECATED

	The two files must be have the same binning. 

	:param RefT: tuple of pytnp instance for the efficiency of reference and the data name
	:type RefT: (pytnp,string)
	:param otherT: tuple pytnp instance for the second efficiency to compare and the data name
	:type otherT: (pytnp,string)
	:param varX: name of the binned variable for the x-axis
	:type varX: string
	:param varY: name of the binned variable for the y-axis
	:type varY: string
	:param Lumi: luminosity
	:param Lumi: string
	:keyword thetitle: title to appear in the canvas
	:type thetitle: string
	:keyword format: ouput format (eps, root, png, ...)
	:type format: string

	:raise RuntimeError: the first two arguments introduced are not tuples (pytnp object, dataname string)
	:raise UserWarning: some of the variables introduced are not binned variables
	:raise AttributeError: dataname not found in the root file
	:raise NameError: the object introduced as pyntp is not a pytnp instance

	"""
	import ROOT
	from math import sqrt
	from plotfunctions import plotMapTH2F
	import rootlogon 
	#---- Initialiting -------------------------------
	# Input keywords and defaults
	KEYWORDS = { 'title': None, 'outputformat': 'eps' }
	
	for key,value in keywords.iteritems():
		try:
			KEYWORDS[key] = value
		except KeyError:
			pass

	if not isinstance(refT,tuple) or not isinstance(otherT,tuple):
		Message = "The two firts arguments must be a tuples '(pytnp object, 'dataname')'"
		printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, Message, RuntimeError )

	tnpRef = refT[0]
	tnp2 = otherT[0] 
	datanameRef = refT[1]
	dataname2 = otherT[1]
	
	datasets = {}
	_index = 0
	for tnp, name in [(tnpRef,datanameRef), (tnp2,dataname2)]:
		try:
			datasets[_index] = tnp.RooDataSet[name]
			for i in [varX, varY]:	
				if not isbinnedVar( datasets[_index], i ):
					message = "Variable '%s' is not a binned variable in the '%s' RooDataSet" % (i, dataname)
					printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, UserWarning )
		except KeyError:
			message = """Invalid dataname '%s', is not in the pytnp instance '%s'""" % (name, tnp)
			printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, AttributeError )
		except AttributeError:
			message = """The object '%s' is not a pytnp instance""" % str(tnp)
			printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, NameError )
		_index += 1
	#---------------------------------------------------
	#--- Name for the histo and for the plot file to be saved
	plotname = tnpRef.resonance+'_'+tnp2.resonance+'_'+tnpRef[datanameRef]['effType']+'_'+tnpRef[datanameRef]['objectType']+'_'+\
			tnpRef[datanameRef]['methodUsed']
	plotName = 'Comparing_'+plotname
	#plotName2 = 'ComparingRelative_'+plotname
	#--- Title for the plot file
	#title2 = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#varepsilon_{'+tnpRef_resLatex+'}'+\
        #                  ' '+tnpRef[datanameRef]['objectType']+' '+dataSet.GetTitle()
	# Dictionary of objects
	#histoList = [ { 'histo': None, 'plotName': plotName, 'effList': [] }, #'title': title},
	#		{ 'histo': None,  'plotName': plotName2, 'effList': [] },# 'title': title2 } 
	#		]
	#--- Checking binned variables  ##################################a
	datasetVarList, effName = getVarNames( datasets[0] )
	
	listTableEff1 = listTableEff( datasets[0] )

	xList = []
	yList = []
	effList = []
	for teff1 in listTableEff1:
		e1,e1lo,e1hi = teff1[effName]
		x,xlo,xhi = teff1[varX]
		y,ylo,yhi = teff1[varY]
		try:		
			e2,e2lo,e2hi = eval('getEff( datasets[1],'+varX+'='+str(x)+','+varY+'='+str(y)+')')
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
		titles[i] = tnpRef[datanameRef]['binnedVar'][i]['latexName']
		unit = tnpRef[datanameRef]['binnedVar'][i]['unit'] 
		if unit != '':
			titles[i] += ' ('+unit+') '
	#k = 0
	XbinsN, arrayX = getBinning( datasets[0].get()[varX] )
	YbinsN, arrayY = getBinning( datasets[0].get()[varY] )
	#histoList[0]['effList'] = effList
	#histoList[|]['effList'] = [ 
	#for hist in histoList:
	ztitle = 'eff'
	title =' CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV ' 
	histoname = plotName#hist['plotName']
	hist = plotMapTH2F( xList, yList, effList, titles[varX], titles[varY], ztitle, XbinsN, arrayX, YbinsN, arrayY, \
				title=title, graphname=histoname, rangeFrame = (0.0, 1.0) )
	#	hist['histo'] = plotMapTH2F( xList, yList, effList, titles[varX], titles[varY], ztitle, XbinsN, arrayX, YbinsN, arrayY, \
	#			title=title, graphname=histoname, rangeFrame = (0.0, 1.0) )

	#-- TH2F ( and TODO: RooDataSet creation)
	mapname = tnpRef.resonance+'_'+tnp2.resonance+'_'+tnpRef[datanameRef]['effType']+'_'+tnpRef[datanameRef]['objectType']+'_'+\
			tnpRef[datanameRef]['methodUsed']
	f = ROOT.TFile( 'effMaps_'+mapname+'_SYS.root' ,'RECREATE')
	if f.IsZombie():
		message = 'Cannot open \'%s\' file. Check your permissions' % fileOut
		printError( diff2DMaps.__module__+'.'+diff2DMaps.__name__, message, IOError )
	#for hist in histoList:
	#	hist['histo'].Write('TH2F_'+hist['plotName']+'_SYS' )
	hist.Write('TH2F_'+histoname+'_SYS' )

	f.Close()



