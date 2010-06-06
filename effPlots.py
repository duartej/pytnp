#!/usr/bin/env python
"""
"""
import ROOT
import pytnp


def getDiff2DPlots( tnpRef, tnp2, *nameOfdataSet ):
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
	title = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#sqrt{#sigma_{'+tnpRef_resLatex+'}^{2}+#sigma_{'+tnp2_resLatex+'}^{2}}'+\
                          ' '+tnpRef.inferInfo(nameOfdataSet)+' '+dataSet.GetTitle()
	plotName2 = 'ComparingRelative_'+tnpRef.resonance+'_'+tnp2.resonance+'_'+nameOfdataSet.replace('/','_')
	#--- Title for the plot file
	title2 = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#varepsilon_{'+tnpRef_resLatex+'}'+\
                          ' '+tnpRef.inferInfo(nameOfdataSet)+' '+dataSet.GetTitle()
	# Dictionary of objects
	histoList = [ { 'histo': None, 'plotName': plotName, 'title': title},
			{ 'histo': None,  'plotName': plotName2, 'title': title2 } 
			]
	#--- Getting the binning and some checks: ##################################
	argSet = dataSet.get()
	pt = argSet['pt'];
	eta = argSet['eta'];
	ptNbins, arrayBinsPt = pytnp.getBinning( pt )
	etaNbins, arrayBinsEta = pytnp.getBinning( eta )
	#------ Checking if the eta bining is the same, otherwise is an error -----@
	argSet2 = dataSet2.get()
	pt2 = argSet2['pt'];
	eta2 = argSet2['eta'];
	ptNbins2, arrayBinsPt2 = pytnp.getBinning( pt2 )
	etaNbins2, arrayBinsEta2 = pytnp.getBinning( eta2 )

	#------ IF a dataset is empty, print a warning a leave the function
	if dataSet.numEntries() == 0:
		print """\033[1;34mThe dataset %s is empty\033[1;m""" % nameOfdataSet
		return 
	if dataSet2.numEntries() == 0:
		print """\033[1;34mThe dataset %s is empty\033[1;m""" % nameOfdataSet
		return 
	############################################################################
	if etaNbins != etaNbins2:
		print """\033[1;31mError: Not supported different eta bin numbers. Exiting...\033[1;m"""
		exit(-1)
	#-- Chosing the minimum size of pt bin
	if ptNbins2 > ptNbins:
		ptNbins = ptNbins2
		arrayBinsPt = arrayBinsPt2
		arrayBinsEta = arrayBinsEta2
		dataSet = dataSet2
	#---------------------------------------------------------------------------@
	#-- To avoid warning in pyROOT
	k = 0
	for thisHisto in histoList:
		hTitleOfHist = 'h'+nameOfdataSet.replace('/','_')+str(k)
		thisHisto['histo'] = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
		thisHisto['histo'].SetTitle( thisHisto['title'] )
		thisHisto['histo'].GetZaxis().SetLimits(0,1.0) # (6.5 Por que??)
		thisHisto['histo'].SetContour(50) # Aumenta el granulado de los colores
		thisHisto['histo'].GetZaxis().SetLabelSize(0.02)
		k += 1
	############### ADDED TO GET QUICK MAPS ##############################
	#th2MAP = histoList[1]['histo'].Clone('sys_diff')
	########### ##### TO FIXME  ##########################################
	#--- Extracting values from reference
	refList = pytnp.tableEff( dataSet )
	for valDict in refList:
		pt = valDict['pt'][0]
		eta = valDict['eta'][0]
		eff = valDict['eff'][0]
		effError = sqrt(valDict['eff'][2]**2.0+valDict['eff'][1]**2.0)  #Simetrizing errors
		other = pytnp.getEff( dataSet2, pt, eta )
		try:
			effOther = other[0]
		#Avoiding empty bins
		except TypeError:
			continue
		effErrorOther = sqrt(other[2]**2.0+other[1]**2.0)               #Simetrizing errors
		finalEff = abs(eff-effOther)
		newErr = sqrt(effErrorOther**2.0+effError**2.0)
		k = 0
		for hist in histoList:
			b = hist['histo'].FindBin( eta, pt )
			if k == 0:
				#--- Sigma map
				try:
					if finalEff/newErr > 10:     #WARNING: Avoiding outliers
						print """ 
Posible outlier: pt= %.4f
		 eta=%.4f
		 eff_ref=%.5f, eff_comp=%.5f
		 |eff_ref-eff_comp|/sigma = %0.5f
		 """ % ( pt,eta,eff,effOther, finalEff/newErr )
					else:
						hist['histo'].SetBinContent( b, finalEff/newErr ) #WARNING
				except ZeroDivisionError:
					hist['histo'].SetBinContent( b, 0.0 )
			elif k == 1:
				#--- Relative map
				try:
					if finalEff/eff > 10:
						print """ 
Posible outlier: pt= %.4f
		 eta=%.4f
		 eff_ref=%.5f, eff_comp=%.5f
		 |eff_ref-eff_comp|eff_ref= %0.5f
		 """ % ( pt,eta,eff,effOther, finalEff/eff )
					else:
						hist['histo'].SetBinContent( b, finalEff/eff )    #WARNING
						#th2MAP.SetBinContent( b, finalEff )    #WARNING
				except ZeroDivisionError:
					pass
					#	hist['histo'].SetBinContent( b, 0.0 ) 
			hist['histo'].SetBinError( b, 0.0 )
			k += 1
	k = 0
	for hist in histoList:
		c = ROOT.TCanvas()
		hist['histo'].GetYaxis().SetTitle('p_{t} (GeV/c)')
		hist['histo'].GetXaxis().SetTitle('#eta')
		hist['histo'].GetZaxis().SetTitle('eff')
		hist['histo'].SetTitle( hist['title'] )
		hist['histo'].Draw('COLZ')
		#--- Only if is sigma plot
		if k >= 0: ###--- FIXME: De momento dejo que esten los valores
			htext = hist['histo'].Clone('htext')
			htext.SetMarkerSize(1.0)
			htext.SetMarkerColor(1)
			ROOT.gStyle.SetPaintTextFormat("1.3f")
			htext.Draw('SAMETEXT0')
		toPlotName = hist['plotName']+'.eps'
		c.SaveAs(toPlotName)
		c.Close()
		k += 1

	########################### TO FIXME ################################################3
	#f = ROOT.TFile('prov_map_sys_diff_'+plotName2+'.root','RECREATE')
	#th2MAP.Write()
	#f.Close()
	### De momento ######################################################################

def doDiffEff( allFiles, refRes, whatPlots ):
	"""
	doCompartionPlots( 'file1,file2,..', 'whatPlots') 

	Given a files names, it will do the plots comparing the efficiencies 
	between the datsets
	"""
	allFiles = allFiles.split(',')
	if len(allFiles) < 2:
		Message = """I need at least 2 input files comma separated without espaces. I read this %s""" % opt.fileName
		parser.error( Message )
	#-- Dictionary of pytnp instance for every resonance
	tnpDict = {}
	#-- List of resonance we have in Latex format
	resonance = {}
	#-- Set to store the names of the histos, no
	#   resonance dependent
	histoSet = set()
	for aFile in allFiles:
		#--- Extract from the standard name file the resonance ---
		#TODO: Pasar el nombre de la resonancia, para poder
		#      usar el constructor adecuado
		resName = pytnp.getResName( aFile )[0]
		if not resName:
			#-- The file name must be standard
			message = """
\033[1;31mError: the file name %s introduced is not in a standard format,
       Resonance_histo[MuFromTrk|Trigger]_....root\033[1;m""" % aFile
                        print message
			exit(-1)
		#---------------------------------------------------------
		#-- Create the pytnp instance
		tnpDict[resName] = pytnp.pytnp( aFile, dataset=whatPlots )
		resonance[ resName ] = tnpDict[resName].resLatex
	#Extract the reference resonance:
	tnpResRef = tnpDict.pop( refRes ) #FIXME: CONTROL DE Errores
	resonanceRef = resonance.pop( refRes )
	for resName,resLatex in sorted(resonance.iteritems()):
		for name in tnpDict[resName].RooDataSet.iterkeys():
			#counting case
			#if name.find('mcTrue') == -1:
			getDiff2DPlots( tnpResRef, tnpDict[resName], name )


def doComparationPlots( allFiles, whatPlots ):
	"""
	doCompartionPlots( 'file1,file2,..', 'whatPlots') 
	"""
	allFiles = allFiles.split(',')
	if len(allFiles) < 2:
		Message = """I need at least 2 input files comma separated without espaces. I read this %s""" % opt.fileName
		parser.error( Message )
	#-- Dictionary of pytnp instance for every resonance
	tnpDict = {}
	#-- List of resonance we have in Latex format
	resonance = {}
	#-- Set to store the names of the histos, no
	#   resonance dependent
	histoSet = set()
	for aFile in allFiles:
		#--- Extract from the standard name file the resonance ---
		try:
			resName = pytnp.getResName( aFile )[0]
		except TypeError:
			#-- The file name must be standard
			message = """
Error: the file name %s introduced is not in a standard format,
       Resonance_histo[MuFromTrk|Trigger]_....root""" % aFile
			exit()
		#---------------------------------------------------------
		#-- Create the pytnp instance
		tnpDict[resName] = pytnp.pytnp( aFile, dataset=whatPlots )
		resonance[ resName ] = tnpDict[resName].resLatex
		#---- Making the plots for this resonance
		for name,rooPlot in tnpDict[resName].RooPlot.iteritems():
			#-- Store the name of the histos
			histoSet.add( name )
			#-- Storing and plotting
			tnpDict[resName].plotEff1D( name )
	#--- In order doing comparations between datasets that have
	#    different binnings we must select the data with LESS
	#    number of binnings. 
	#----WARNING: the user must check that he/she is using the
	#    same binnings FIXME: Check this automatically
	#FIXME: NOT WORKS--> I don't know
	print len(histoSet)
	minRooPlotTuple = [ (len(x.RooPlot), x.RooPlot) for x in tnpDict.itervalues() ] # pairing lenght with names of RooPlots
	minValue = min( map( lambda x: x[0], minRooPlotTuple ) )                        # getting the smallest RooPlot
	minRooPlot = filter( lambda x: minValue == x[0], minRooPlotTuple )[0][1]        # extracting the RooPlot
	minNamesList = set( [ i for i in minRooPlot.iterkeys() ]) 
	histoSet = histoSet.intersection( minNamesList )
	print len(histoSet)
	#exit(-1)
	#--- Plots for the all resonances
	#-- Assuming we have the same names for histos in every
	#   dict, but the first word (resonance dependent).
	for histo in histoSet:			
		c = ROOT.TCanvas()
		leg = ROOT.TLegend(0.8,0.15,0.98,0.3)
		inSame = '' 
		#-- How much resonances? To save the plot..
		howMuchRes = ''
		hMRLatex = ''
		hframe = None
		color = [ 1, 38, 46, 28, 30 ] 
		title = ''
		i = 0
		for resName,resLatex in sorted(resonance.iteritems()):
			#Preparing the histo and draw
			howMuchRes += resName
			hMRLatex += resLatex+' '
			#-- Avoiding different binnings
			try:
				htmp = tnpDict[resName][histo]
			except KeyError:
				print """\033[1;31mWarning: There is no plot %s for the resonance %s\033[1;m""" % ( histo,resName)
				continue
			#Setting the frame, once
			if not hframe:
				axisX = htmp.GetXaxis()
				rangesX = ( axisX.GetBinLowEdge( axisX.GetFirst() ),\
					axisX.GetBinUpEdge( axisX.GetLast() ) )
				hframe = c.DrawFrame(rangesX[0], 0, rangesX[1], 1 )
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
			#hframe.SetTitle( title ) 
			htmp.Draw( 'P'+inSame )
			leg.AddEntry( htmp, resLatex, 'P' )
			inSame = 'SAME'
			i += 1
		leg.Draw()
		#-- includes all resonances
		title = hMRLatex+', '+title
		hframe.SetTitle( title )
		c.SaveAs(howMuchRes+histo.replace('/','_')+'.eps')
		c.Close()


def sysMCFIT(_file):
        """
	sysMCFIT( 'namerootfile' ) 
        """
        ROOT.gROOT.SetBatch(1)
	
	#TODO: Permitir que se puedan entrar dos ficheros
	#      Ahora mc debe estar en el mismo fichero
	tnp = pytnp.pytnp(_file)

	effList = tnp.getFitEffList()
	
	pairFitMC = [ (tnp.getCountMCName(i),i) for i in effList ]
	##- Checking if there are MC true info
	for i in filter( lambda (mc,fitEff): not mc, pairFitMC ):
		message = '\n'
		message += """\033[1;31mERROR: The %s does not contains MC True information\033[1;m""" % _file
		message += '\n'
		print message
		exit(-1)

	for tMC, tFit in pairFitMC:
		getDiff2DPlots( tnp, tnp, tMC, tFit )

if __name__ == '__main__':
	"""
	"""
        from optparse import OptionParser

        parser = OptionParser()
	parser.set_defaults(counting=False)
        parser.add_option( '-i', '--input', action='store', dest='fileName', help='Input root file name, comma separated, no espaces' )
        parser.add_option( '-u', '--AllUpsilons', action='store_true', dest='allUpsilons', help='Make all upsilons comparations' )
        parser.add_option( '--dim1', action='store_true', dest='dim1Plots', help='Must I do 1-dim plots?' )
        parser.add_option( '--dim2', action='store_true', dest='dim2Plots', help='Must I do 2-dim plots?' )
	parser.add_option( '-c', '--comp', action='store', dest='resToComp', metavar='RESONANCE', help='Do the comparation between efficiencies for different resonances taking RESONANCE as reference' )
        parser.add_option( '--counting', action='store_true', dest='counting', help='If active this flag, do the plots using the MC information (counting events)' )
        parser.add_option( '--sysTnP', action='store_true', dest='sysTnP', help='Do the plots and a root file maps for the differences between counting MC and Tag and Probe fit efficiencies.' )
        parser.add_option( '-m', '--maps', action='store', dest='maps', help='Create root files with TH2F and RooDataSets, give the name of the objet' )
        parser.add_option( '-t', '--tables', action='store_true', dest='tables', help='Create latex tables from a efficiency maps root files' )

        ( opt, args ) = parser.parse_args()

	if not opt.fileName:
		Message="""Missed mandatory argument -i FILENAME"""
		parser.error( Message )
	
	import pytnp
	import rootlogon

	#Do not display graphics
	pytnp.ROOT.gROOT.SetBatch(1)
	#Using MC info-- counting events instead of fit
	whatPlots = 'fit_eff'
	if opt.counting:
		whatPlots = 'cnt_eff'

	if opt.allUpsilons:
		allFiles = opt.fileName
		doComparationPlots( allFiles, whatPlots )

	if opt.resToComp:
		#--- 
		allFiles = opt.fileName
		#FIXME: Control de errores
		doDiffEff( allFiles, opt.resToComp, whatPlots )
	
	if opt.dim1Plots and not opt.allUpsilons:
		tnp = pytnp.pytnp(opt.fileName, dataset=whatPlots)
		resonance = tnp.resLatex
		try:
			for name,rootPlot in tnp.RooPlot.iteritems():
				#Counting case:
				#if name.find('mcTrue') == -1:
				tnp.plotEff1D(name)
		except AttributeError:
			for name, tcanvas in tnp.TCanvas.iteritems():
				if name.find('_PLOT_') != -1 and (name.find('pt_eta_') == -1 or name.find('eta_pt') == -1):
					tnp.plotEff1D(name)
		del tnp

	if opt.dim2Plots or opt.maps:
		tnp = pytnp.pytnp(opt.fileName, dataset=whatPlots)
		#resonance = tnp.resLatex
		for name,dataSet in tnp.RooDataSet.iteritems():
			#if name.find('mcTrue') == -1:
			tnp.plotEff2D(name)
		if opt.maps:
			#FIXME: De momento paso el valor del objecto
			maps=opt.maps
			#FIXME: Por el momento
			if opt.fileName.find('MuFromTk') != -1:
				effType = 'MuonID'
			elif opt.fileName.find('TriggerFromGlb') != -1:
				effType = 'TriggerFromGlb'
			elif opt.fileName.find('TriggerFromTrk') != -1:
				effType = 'TriggerFromTk'
			elif opt.fileName.find('TriggerFrom') != -1:
				effType = 'Trigger'
			#FIXME: De momento paso el valor del objecto
			tnp.write('effMaps_'+tnp.resonance+'_'+effType+'_'+maps+'.root' )
		del tnp

	if opt.sysTnP:
		sysMCFIT( opt.fileName )

	if opt.tables:
		#FIXME Control de errores
		f = ROOT.TFile( opt.fileName )
		dataList = [ f.Get(i.GetName()) for i in f.GetListOfKeys() if i.GetClassName() == 'RooDataSet' ]
		if len(dataList) == 0:
			print """\033[1;33mWarning: the file %s do not contain a efficiency map\033[1;m""" % opt.fileName 
		for d in dataList:
			pytnp.tableLatex(d)
		#--------------------------------------------------


		
	

	



