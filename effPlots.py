#!/usr/bin/env python
"""
"""
import sys
if sys.version_info < (2,6):
	print """\033[1;31mError: you must use python 2.6 or greater.\033[1;m
Check you have init the CMSSW environment: 
	$ cd /whereeverItIs/CMSSW/CMSSW_X_Y_Z/src
	$ cmsenv"""
	sys.exit(-1)

import ROOT
import pytnp
from pytnp.utils.tnputils import getDiff2DPlots

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
	#histoSet = set()
	for aFile in allFiles:
		#--- Extract from the standard name file the resonance ---
		#TODO: Pasar el nombre de la resonancia, para poder
		#      usar el constructor adecuado
		resName = getResName( aFile )[0]
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
	try:
		tnpResRef = tnpDict.pop( refRes )
		
	except KeyError:
		message ="""
\033[1;31mError: the resonance name '%s' introduced is wrong, use either of %s \033[1;m""" % (refRes, [i for i in tnpDict.iterkeys()]) 
		print message
		raise KeyError
	resonanceRef = resonance.pop( refRes )
	for resName,resLatex in sorted(resonance.iteritems()):
		for name in tnpDict[resName].RooDataSet.iterkeys():
			#counting case
			#if name.find('mcTrue') == -1:
			getDiff2DPlots( tnpResRef, tnpDict[resName], Lumi, name )


def doComparationPlots( allFiles, whatPlots, Lumi ):
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
	#-- Set to store the Vnames of the histos, no
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
		for name in tnpDict[resName].RooDataSet.iterkeys():
			#-- Store the name of the RooDataSet
			histoSet.add( name )
			#-- Storing and plotting
			tnpDict[resName].plotEff1D( name, Lumi )
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
				graphName.append( (NAMErds,NAMEgraph) )
	#--- Plots for the all resonances
	#-- Assuming we have the same names for histos in every
	#   dict, but the first word (resonance dependent).
	for RDSNAME,GRAPHNAME in graphName:			
		c = ROOT.TCanvas()
		#-----------FIXME: CLARA PATCH ----------------------#
		text = ROOT.TPaveText(0.6,0.4,0.8,0.6,"NDC")
		text.AddText('CMS Preliminary,  #sqrt{s}= 7 TeV')
		if Lumi != '':
			text.AddText('#int#font[12]{L}dt = '+str(Lumi)+' nb^{-1}')
		text.SetBorderSize(0)
		text.SetFillColor(0)
		text.SetTextSize(0.04);
		#------------------ END CLARA PATCH -----------------#
		leg = ROOT.TLegend(0.6,0.25,0.8,0.4)
		inSame = '' 
		#-- How much resonances? To save the plot..
		howMuchRes = ''
		hMRLatex = ''
		hframe = None
		color = [ 1, 38, 46, 28, 30 ] 
		typeMarker = [ 20, 21, 22, 23, 24 ]
		title = ''
		i = 0
		for resName,resLatex in sorted(resonance.iteritems()):
			#Preparing the histo and draw
			howMuchRes += resName
			hMRLatex += resLatex+' '
			#-- Avoiding different binnings
			try:
				htmp = tnpDict[resName][RDSNAME]['tgraphs'][GRAPHNAME]
			except KeyError:
				print """\033[1;31mWarning: There is no graph %s for the resonance %s\033[1;m""" % ( GRAPHNAME,resName)
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
		leg.Draw()
		text.Draw()
		#-- includes all resonances
		title = hMRLatex+', '+title
		#hframe.SetTitle( title )--> No titles
		#hframe.SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
		c.SaveAs(howMuchRes+GRAPHNAME+'.eps')
		c.Close()


def sysMCFIT(_file):
        """
	sysMCFIT( 'namerootfile' ) 

	Compute the differences between MC True counting efficiency
	and Tag and Probe fitted efficiency. Return plots and 
	(TODO) root file containing maps of the absolute differencies
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
		getDiff2DPlots( tnp, tnp, Lumi, tMC, tFit )


if __name__ == '__main__':
	"""
	"""
        from optparse import OptionParser

        parser = OptionParser()
	parser.set_defaults(counting=False)
        parser.add_option( '-i', '--input', action='store', dest='fileName', help='Input root file name, comma separated, no espaces' )
        parser.add_option( '-u', action='store_true', dest='allUpsilons', help='1-dim plots comparing different efficiencies from different root files' )
        parser.add_option( '--dim1', action='store_true', dest='dim1Plots', help='Must I do 1-dim plots?' )
        parser.add_option( '--dim2', action='store_true', dest='dim2Plots', help='Must I do 2-dim map plots?' )
	parser.add_option( '-c', '--comp', action='store', dest='resToComp', metavar='RESONANCE', help='Comparation between efficiencies for different resonances taking RESONANCE as reference, plots of relative and absolute efficiencies' )
        parser.add_option( '--counting', action='store_true', dest='counting', help='If active this flag, do the plots using the MC information (counting events)' )
        parser.add_option( '--sysTnP', action='store_true', dest='sysTnP', help='Do the plots (and a root file maps--Not yet) for the differences between counting MC and Tag and Probe fit efficiencies.' )
        parser.add_option( '-m', '--maps', action='store', dest='maps', metavar='CATEGORY', help='Create root files with TH2F and RooDataSets, give the name of the muon category' )
        parser.add_option( '-t', '--tables', action='store_true', dest='tables', help='Create latex tables from an efficiency map root file' )
        parser.add_option( '-L', '--lumi', action='store', dest='Lumi', help='Integrated Luminosity (in nbar^{-1}' )

        ( opt, args ) = parser.parse_args()

	if not opt.fileName:
		Message="""Missed mandatory argument -i FILENAME"""
		parser.error( Message )
	
	import pytnp
	from pytnp.utils.getresname import *
	from pytnp.utils.tnputils import *
	import pytnp.utils.rootlogon

	#Store luminosity if is provided
	Lumi = ''
	if opt.Lumi:
		Lumi = ' L_{int}='+str(opt.Lumi)+' nb^{-1} '

	#Do not display graphics
	ROOT.gROOT.SetBatch(1)
	#Using MC info-- counting events instead of fit
	whatPlots = 'fit_eff'
	if opt.counting:
		whatPlots = 'cnt_eff'

	if opt.allUpsilons:
		allFiles = opt.fileName
		#--- FIXME: Provisional
		Lumi2 = Lumi
		if opt.Lumi:
			Lumi2 = opt.Lumi
		doComparationPlots( allFiles, whatPlots, Lumi2 )

	if opt.resToComp:
		#--- 
		allFiles = opt.fileName
		#FIXME: Control de errores
		doDiffEff( allFiles, opt.resToComp, whatPlots )
	
	if opt.dim1Plots and not opt.allUpsilons:
		tnp = pytnp.pytnp(opt.fileName, dataset=whatPlots)
		resonance = tnp.resLatex
		try:
			for name,dataset in tnp.RooDataSet.iteritems():
				#Counting case:
				#if name.find('mcTrue') == -1:
				tnp.plotEff1D(name,Lumi)
		except AttributeError:
			for name, tcanvas in tnp.TCanvas.iteritems():
				if name.find('_PLOT_') != -1 and (name.find('pt_eta_') == -1 or name.find('eta_pt') == -1):
					tnp.plotEff1D(name,Lumi)
		del tnp

	if opt.dim2Plots or opt.maps:
		tnp = pytnp.pytnp(opt.fileName, dataset=whatPlots)
		#resonance = tnp.resLatex
		for name,dataSet in tnp.RooDataSet.iteritems():
			#if name.find('mcTrue') == -1:
			tnp.plotEff2D(name,Lumi)
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
			print """\033[1;33mWarning: the file %s does not contain a efficiency map\033[1;m""" % opt.fileName 
		for d in dataList:
			pytnp.tableLatex(d)
		#--------------------------------------------------


		
	

	



