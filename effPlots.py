#!/usr/bin/env python
"""
"""
import ROOT
import pytnp

def getResName( aFile ):
	"""
	"""
	import re

	regexp = re.compile( '\D*(?P<NUMBER>\dS)' )
	resonance = ''
	try:
		num = regexp.search( aFile ).group( 'NUMBER' )
		resonance = 'Upsilon'+num
	except AttributeError:
		if aFile.find( 'JPsi' ) != -1:
			resonance = 'JPsi'
		elif aFile.find( 'Upsilon' ) != -1:
			resonance = 'AllUpsilons'
	except:
		return None

	return resonance


def getDiff2DPlots( tnpRef, tnp2, nameOfdataSet, nameOfdataSet2='' ):
	"""
	"""
	from math import sqrt
	####--FIXME: PAtch para poder hacer mc-fit y res1-res2
	if nameOfdataSet2=='':
		nameOfdataSet2=nameOfdataSet
		tnpRef_resLatex = tnpRef.resLatex
		tnp2_resLatex =  tnp2.resLatex
	else:
		tnpRef_resLatex = tnpRef.resLatex+'^{MC}'
		tnp2_resLatex = tnpRef.resLatex+'^{TnP}'
        try:
		dataSet = tnpRef.RooDataSet[nameOfdataSet]
	except KeyError:
		print """Error: you must introduce a valid name"""
		raise KeyError
        try:
		dataSet2 = tnp2.RooDataSet[nameOfdataSet2]
	except KeyError:
		print """Error: you must introduce a valid name"""
		raise KeyError
	##---- FIXME---> HARDCODED para MC y Fit comparation
	#--- Name for the histo and for the plot file to be saved
	plotName = 'Comparing_'+tnpRef.resonance+'_'+tnp2.resonance+'_'+nameOfdataSet.replace('/','_')
	#--- Title for the plot file
	title = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#sqrt{#sigma_{'+tnpRef_resLatex+'}^{2}+#sigma_{'+tnp2_resLatex+'}^{2}}'+\
                          ' '+tnpRef.inferInfo(nameOfdataSet)+' '+dataSet.GetTitle()
	plotName2 = 'ComparingRelative_'+tnpRef.resonance+'_'+tnp2.resonance+'_'+nameOfdataSet.replace('/','_')
	#--- Title for the plot file
	title2 = '|#varepsilon_{'+tnpRef_resLatex+'}'+'-#varepsilon_{'+tnp2_resLatex+'}|/#varepsilon_{'+tnpRef_resLatex+'}'+\
                          ' '+tnpRef.inferInfo(nameOfdataSet)+' '+dataSet.GetTitle()
	#--- Getting the binning: must I check if tnp2 has the same binning?
	argSet = dataSet.get()
	pt = argSet['pt'];
	eta = argSet['eta'];
	ptNbins, arrayBinsPt = pytnp.getBinning( pt )
	etaNbins, arrayBinsEta = pytnp.getBinning( eta )
	#-- To avoid warning in pyROOT
	hTitleOfHist = 'h'+nameOfdataSet.replace('/','_')
	h = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
	h.SetTitle( title )
	h.GetZaxis().SetLimits(0,6.5)
        h.SetContour(50) # Aumenta el granulado de los colores
        ##--- 
	h2 = ROOT.TH2F( hTitleOfHist+'rel', '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
	h2.SetTitle( title2 )
        h2.SetContour(50)
	h2.GetZaxis().SetLimits(0.0,1.0)
	h2.GetZaxis().SetLabelSize(0.02)
	#####################################################h2.GetZaxis().SetLimits(0,6.5)
	#First I fill the content of tnpRef
	refList = pytnp.tableEff( dataSet )
	for valDict in refList:
		pt = valDict['pt'][0]
		eta = valDict['eta'][0]
		eff = valDict['eff'][0]
		effError = (valDict['eff'][2]-valDict['eff'][1])/2.0 #WATCH: Error 'simetrized'
		b = h.FindBin( eta, pt )
		h.SetBinContent( b, eff )
		h.SetBinError( b, effError )
		b = h2.FindBin( eta, pt )
		h2.SetBinContent( b, eff )
		h2.SetBinError( b, effError )
	#Now I get the content of tnp2 in order to do the difference
	toComp = pytnp.tableEff( dataSet2 )
	for valDict in toComp:
		pt = valDict['pt'][0]
		eta = valDict['eta'][0]
		eff = valDict['eff'][0]
		effError = (valDict['eff'][2]-valDict['eff'][1])/2.0 #WATCH: Error 'simetrized'
		b = h.FindBin( eta, pt )
		oldVal = h.GetBinContent( b )
		newVal = abs(oldVal-eff)
		oldErr = h.GetBinError( b )
		newErr = sqrt(oldErr**2.0+effError**2.0)
		#print pt, eta, newVal, oldVal
		try:
			h.SetBinContent( b, newVal/newErr )
		except ZeroDivisionError:
			h.SetBinContent( b, 0 )
		h.SetBinError( b, 0.0 )  ##WATCH: Missed error propagation
                #####----- EL otro histograma
		oldVal = h2.GetBinContent( b )
		newVal = abs(oldVal-eff)
		try:
		        #FIXME: Cuidado con esto!!
		        if newVal/oldVal > 10.0:
				pass
			else:
				h2.SetBinContent( b, newVal/oldVal )
		except ZeroDivisionError:
			h2.SetBinContent( b, 0 )
		h2.SetBinError( b, 0.0 )  ##WATCH: Missed error propagation
		
	c = ROOT.TCanvas()
	h.GetYaxis().SetTitle('p_{t} (GeV/c)')
	h.GetXaxis().SetTitle('#eta')
	h.GetZaxis().SetTitle('eff')
	h.SetTitle( title )
	h.Draw('COLZ')
	htext = h.Clone('htext')
	htext.SetMarkerSize(1.0)
	htext.SetMarkerColor(1)
	ROOT.gStyle.SetPaintTextFormat("1.3f")
	htext.Draw('SAMETEXT0')
	toPlotName = plotName+'.eps'
	c.SaveAs(toPlotName)
        c.Close()
	#------------------ El otro....
	c2 = ROOT.TCanvas()
	h2.GetYaxis().SetTitle('p_{t} (GeV/c)')
	h2.GetXaxis().SetTitle('#eta')
	h2.GetZaxis().SetTitle('eff')
	h2.SetTitle( title2 )
	h2.Draw('COLZ')
	#htext = h2.Clone('htext')
	#htext.SetMarkerSize(1.0)
	#htext.SetMarkerColor(1)
	#ROOT.gStyle.SetPaintTextFormat("1.3f")
	#htext.Draw('SAMETEXT0')
	toPlotName2 = plotName2+'.eps'
	c2.SaveAs(toPlotName2)

def doDiffEff( allFiles, refRes, whatPlots ):
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
			resName = getResName( aFile )
		except TypeError:
			#-- The file name must be standard
			message = """
Error: the file name %s introduced is not in a standard format,
       Resonance_histo[MuFromTrk|Trigger]_....root""" % aFile
			exit()
		#---------------------------------------------------------
		#-- Create the pytnp instance
		tnpDict[resName] = pytnp.pytnp( aFile, whatPlots )
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
			resName = getResName( aFile )
		except TypeError:
			#-- The file name must be standard
			message = """
Error: the file name %s introduced is not in a standard format,
       Resonance_histo[MuFromTrk|Trigger]_....root""" % aFile
			exit()
		#---------------------------------------------------------
		#-- Create the pytnp instance
		tnpDict[resName] = pytnp.pytnp( aFile, whatPlots )
		resonance[ resName ] = tnpDict[resName].resLatex
		#---- Making the plots for this resonance
		for name,rooPlot in tnpDict[resName].RooPlot.iteritems():
			#--- Don't plot mcTrue information--> YES, counting case
			#if name.find('mcTrue') == -1:
			#-- Store the name of the histos
			histoSet.add( name )
			#-- Storing and plotting
			tnpDict[resName].plotEff1D( name )
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
			htmp = tnpDict[resName][histo]
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
        """
	message = """
===============================================================
                          WARNING !!
===============================================================
           This script is hardcoded... Waiting for
                        generalization.
                       Use with caution.
	"""
	print message

        ROOT.gROOT.SetBatch(1)

        ###HARDCODED FIXME: Funciona pero ojo!! hay que arreglarlo
        #################################
	#_file = _file[0]
        tnp = pytnp.pytnp(_file)

        #COMPRUEBA ESTO----
        #buildBin = lambda x: format(x*2.5/24.0,'.2f')+' < #eta < '+format((x+1)*2.5/24.0,'.2f')
        #binsEta = dict( [ (str(i),buildBin(i)) for i in xrange(25) ] )

        #binsEta = { '0' : '-2.4 < #eta < -1.6', '1' : '-1.6 < #eta < -1.0', '2' : '-1.0 < #eta < -1.0',\
        #               '3' : '1.0 < #eta < 1.6', '4' : '1.6 < #eta < 2.4' }

        fit = []
        mcTrue = []
        for i in tnp.RooDataSet.iterkeys():
                if i.find('fit_eff') != -1:
                        fit.append( i )
                if i.find('cnt_eff') != -1:
                        mcTrue.append( i )

        #Building the datasets pairs
        #--- TODO: hay una manera mas eficiente de hacer esto (filter, map...)
        pairFitMC = []
        for MC in mcTrue:
                for FIT in fit:
                        if MC.strip('_mcTrue/cnt_eff') == FIT.strip('/fit_eff'):
                                pairFitMC.append( (MC,FIT) )
	
	for tMC, tFIT in pairFitMC:
		getDiff2DPlots( tnp, tnp, tMC, tFIT )
		


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
        parser.add_option( '--sysTnP', action='store_true', dest='sysTnP', help='Compute differences between mcTrue counting and TnP-fit' )

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
		tnp = pytnp.pytnp(opt.fileName, whatPlots)
		resonance = tnp.resLatex
		for name,rootPlot in tnp.RooPlot.iteritems():
			#Counting case:
			#if name.find('mcTrue') == -1:
			tnp.plotEff1D(name)
		del tnp

	if opt.dim2Plots:
		tnp = pytnp.pytnp(opt.fileName, whatPlots)
		resonance = tnp.resLatex
		for name,dataSet in tnp.RooDataSet.iteritems():
			#if name.find('mcTrue') == -1:
			tnp.plotEff2D(name)
		del tnp

	if opt.sysTnP:
		sysMCFIT( opt.fileName )

	



