"""
Function utilities which uses the pytnp class to do several plots
  TODO: Description
"""

import ROOT

from pytnp.libPytnp.tnputils import  *

def superImposed( tnpDict, variable, whatPlots, Lumi, **keywords ):
	"""
	superImposed( { resName1: tnp1, resName2: tnp2,...} , 'variable', whatPlots, Lumi ) 
	
	Giving different pytnp instances, the function do the 1-dim plots of the 'variable'
	in the same canvas. The pytnp instances must have the same object types (objectType)
	(ex: Global muon identification efficiency, ...) with the SAME name.
	See the objectType content of a pytnp instance usign the print function for a
	pytnp instance. 
	"""
	#FIXME: Esta acabada?? Codigo enrevesado...
	#from pytnp.steerplots.plotfunctions import plotAsymGraphXY,legend
	import rootlogon
	#-- Checking we have the same efficiency object for each instance

	#-- Set to store the names of the histos, no
	#   resonance dependent
	histoSet = set()
	#---- Making the plots for this resonance 
	for resName, tnp in tnpDict.iteritems():
		for name in tnp.RooDataSet.iterkeys():
			#-- Store the name of the RooDataSet
			histoSet.add( name )
			#-- Storing and plotting
			tnp.plotEff1D( name, variable, Lumi )
	#--- In order doing comparations between datasets that have
	#    different binnings we must select the data with LESS
	#    number of binnings. 
	#----WARNING: the user must check that he/she is using the
	#    same binnings FIXME: Check this automatically
	#FIXME: NOT WORKS--> I don't know
#	print len(histoSet)
#	minRooDataSetTuple = [ (len(x.RooDataSet, x.RooDataSet) for x in tnpDict.itervalues() ] # pairing lenght with names of RooPlots
#	minValue = min( map( lambda x: x[0], minRooDataSetTuple ) )                        # getting the smallest RooPlot
#	minRooDataSet = filter( lambda x: minValue == x[0], minRooDataSetTuple )[0][1]        # extracting the RooPlot
#	minNamesList = set( [ i for i in minRooDataSet.iterkeys() ]) 
#	histoSet = histoSet.intersection( minNamesList )
	graphName = []
	for __tnp in tnpDict.itervalues():
		for NAMErds, DICT in __tnp.iteritems():
			for NAMEgraph in DICT['tgraphs'].iterkeys():
				# Skipping the resonance name
				graphName.append( (NAMErds,NAMEgraph.replace(__tnp.resonance+'_','')) )
	#--- Plots for the all resonances
	#-- Assuming we have the same names for histos in every
	#   dict, but the first word (resonance dependent).
	howPlottedGraphs = 0
	for RDSNAME,GRAPHNAME in graphName:			
		c = ROOT.TCanvas()
		#-----------FIXME: CLARA PATCH ----------------------#
		text = ROOT.TPaveText(0.6,0.4,0.8,0.6,"NDC")
		text.AddText('CMS Preliminary,'+Lumi+'  #sqrt{s}= 7 TeV')
		text.SetBorderSize(0)
		text.SetFillColor(0)
		text.SetTextSize(0.04);
		#------------------ END CLARA PATCH -----------------#
		leg = ROOT.TLegend(0.6,0.25,0.8,0.4)
		#leg = legend( 'DR')
		inSame = '' 
		#-- How much resonances? To save the plot..
		howMuchRes = ''
		hMRLatex = ''
		hframe = None
		color = [ 1, 38, 46, 28, 30 ] 
		typeMarker = [ 20, 21, 22, 23, 24 ]
		title = ''
		i = 0
		howMuchLost = 0
		for resName,tnp in sorted(tnpDict.iteritems()):
			#Preparing the histo and draw
			howMuchRes += resName
			hMRLatex += tnp.resLatex+' '
			resLatex = tnp.resLatex
			#-- Avoiding different binnings
			try: 
				#Adding the resonance name
				htmp = tnp[RDSNAME]['tgraphs'][tnp.resonance+'_'+GRAPHNAME]
			except KeyError:
				print """\033[1;33mWarning: There is no graph '%s' for the resonance '%s'\033[1;m""" % ( GRAPHNAME,resName)
				howMuchLost += 1
				continue
			#Setting the frame, once
			if not hframe:
				axisX = htmp.GetXaxis()
				rangesX = ( axisX.GetBinLowEdge( axisX.GetFirst() ),\
					axisX.GetBinUpEdge( axisX.GetLast() ) )
				hframe = c.DrawFrame( rangesX[0], 0, rangesX[1], 1.1 )
				hframe.GetXaxis().SetTitle( htmp.GetXaxis().GetTitle() )
				hframe.GetYaxis().SetTitle( htmp.GetYaxis().GetTitle() )
				#-- Extract the resonance --------------
				tmpTitle = htmp.GetTitle().split(' ')[1:]
				joinT = lambda x,y : x+' '+y
				title = ''
				for k in tmpTitle:
					title = joinT(title,k)
			htmp.SetLineColor(color[i])
			htmp.SetMarkerColor(color[i])
			htmp.SetMarkerStyle(typeMarker[i])
			#hframe.SetTitle( title ) 
			htmp.Draw( 'P'+inSame )
			leg.AddEntry( htmp, resLatex, 'P' )
			inSame = 'SAME'
			i += 1
		#-- If fail all the graphs, don't print (Always do the first one, so howMuchLost+1)
		if howMuchLost+1 == len(tnpDict):
			print """\033[1;33mWarning: --->Skipping the graph creation for '%s' \033[1;m""" % ( howMuchRes+GRAPHNAME)
			continue
		leg.Draw()
		text.Draw()
		#-- includes all resonances
		title = hMRLatex+', '+title
		#hframe.SetTitle( title )--> No titles
		#hframe.SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
		c.SaveAs(howMuchRes+GRAPHNAME+'.eps')
		c.Close()
		howPlottedGraphs += 1
	
	#-- If there no plotted graph, the user possibly misunderstood the functionality of this function
	if howPlottedGraphs == 0:
		print """ """
		print """\033[1;39mCAVEAT: No graph has been plotted! The correct use of this function implies\n\033"""\
				"""        that the root files involved contains the same object type efficiency.\n"""\
				"""        (See the contents of a pytnp instance, for example  effPlots -p -i rootfile.root)\n"""\
				"""        and look the 'objectType' key from the output\033[1;m"""
		# Raise a exception ??


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
	import rootlogon 
	#from pytnp.libPytnp.tnputils import checkbinnedVar
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
	
	listTableEff1 = listTableEff( dataSet )
	for teff1 in listTableEff1:
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


def diffEffMaps( tnpDict, refRes, Lumi, **keywords ):
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
			getDiff2DPlots( tnpResRef, tnpDict[resName], Lumi, name )





def sysMCFIT(tnp, Lumi, **keywords):
        """
	sysMCFIT( 'namerootfile' ) 

	Compute the differences between MC True counting efficiency
	and Tag and Probe fitted efficiency. Return plots (and 
	(TODO) root file) containing maps of the absolute differencies
        """
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
		getDiff2DPlots( tnp, tnp, Lumi, tMC, tFit )

