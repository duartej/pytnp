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

if __name__ == '__main__':
	"""
	"""
        from optparse import OptionParser

        parser = OptionParser()
	parser.set_defaults(counting=False,effName='efficiency')
        parser.add_option( '-i', '--input', action='store', dest='fileName', help='Input root file name, comma separated, no espaces' )
        parser.add_option(  '--resName', action='store', dest='resName', help='Resonance name for the files introduced with -i option (same order)' )
	parser.add_option( '--content', action='store_true', dest='printContent', help='Print the Tag and Probe content of the root file(s) showing'\
                ' their encapsulate structure and the exit ' )
        parser.add_option( '-u', action='store_true', dest='allUpsilons', help='1-dim plots comparing different efficiencies from different root files' )
        parser.add_option( '--dim1', action='store_true', dest='dim1Plots', help='Must I do 1-dim plots?' )
        parser.add_option( '--dim2', action='store_true', dest='dim2Plots', help='Must I do 2-dim map plots?' )
	parser.add_option( '-c', '--comp', action='store', dest='resToComp', metavar='RESONANCE', help='Comparation between efficiencies for different resonances taking RESONANCE as reference, plots of relative and absolute efficiencies' )
        parser.add_option( '--counting', action='store_true', dest='counting', help='If active this flag, do the plots using the MC information (counting events)' )
        parser.add_option( '--sysTnP', action='store_true', dest='sysTnP', help='Do the plots (and a root file maps--Not yet) for the differences between counting MC and Tag and Probe fit efficiencies.' )
        parser.add_option( '-m', '--maps', action='store', dest='maps', metavar='CATEGORY', help='Create root files with TH2F and RooDataSets, give the name of the muon category' )
        parser.add_option( '-t', '--tables', action='store_true', dest='tables', help='Create latex tables from an efficiency map root file' )
        parser.add_option( '-L', '--lumi', action='store', dest='Lumi', nargs=2 help='Integrated Luminosity and unit' )
	parser.add_option( '-e', '--effName', action='store', dest='effName', help='Efficiency name as will found in the rootfile (CAVEAT: The same name'\
                ' for all RooDataSet in the rootfile is mandatory)' )

        ( opt, args ) = parser.parse_args()

	if not opt.fileName:
		Message="""Missed mandatory argument -i FILENAME"""
		parser.error( Message )
	
	from pytnp.libPytnp.pytnpclass import pytnp
	#from pytnp.libPytnp.getresname import getresname
	#from pytnp.libPytnp.tnputils import *
	#import pytnp.libPytnp.rootlogon

	#Print content and exit
	if opt.printContent:
                allFiles = opt.fileName.split(',')
                if len(allFiles) < 1:
                        Message = """I need at least 1 input files comma separated without espaces. I parsed '%s'""" % opt.fileName
                        parser.error( Message )
                for _f in allFiles:
                        tnp = pytnp( _f, effName = opt.effName)
                        print tnp

	#Store luminosity if is provided
	Lumi = ''
	if opt.Lumi:
		Lumi = ' L_{int}='
		for val in opt.Lumi:
			Lumi += str(opt.Lumi)+' '

	#Using MC info-- counting events instead of fit
	whatPlots = 'fit_eff'
	if opt.counting:
		whatPlots = 'cnt_eff'
	
	#Do not display graphics
	import ROOT
	ROOT.gROOT.SetBatch(1)

	if opt.allUpsilons:
		allFiles = opt.fileName
		#--- FIXME: Provisional
		Lumi2 = Lumi
		if opt.Lumi:
			Lumi2 = opt.Lumi
		doComparationPlots( allFiles, whatPlots, Lumi2 )

	if opt.resToComp:
		from steerplots.plotsCreation import diffEff
		from steer
		#--- 
		allFiles = opt.fileName.split(',')
		if len(allFiles) < 2:
			Message = """I need at least 2 input files comma separated without espaces. I read this %s""" % opt.fileName
			parser.error( Message )
		#--- Has the user introduced the resonance name?
		try:
			resNameLists = opt.resName.split(',')
		except AttributeError:
			resNameList = []
		#-- Dictionary of pytnp instance for every resonance
		tnpDict = {}
			
		for aFile, resname in map( lambda _file,_resName: (x,y), allFiles,resNameList ):
			#--- Extract from the standard name file the resonance ---
			if not resname:
				# resonance name and latex format name
				resNameTuple = getResName( aFile )
			else:
				resNameTuple = ( resname, resname)
			tnpDict[resName[0]] = pytnp( aFile, dataset=whatPlots, effName=opt.effName, resonance=resNameTuple )

		#--- Ready to run the plots
		diffEff( tnpDict, opt.resToComp, Lumi )
	
	if opt.dim1Plots and not opt.allUpsilons:
		tnp = pytnp(opt.fileName, dataset=whatPlots)
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
		tnp = pytnp(opt.fileName, dataset=whatPlots)
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


		
	

	



