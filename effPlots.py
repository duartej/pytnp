#!/usr/bin/env python
"""
"""
import ROOT

def getResName( aFile ):
	"""
	"""
	import re

	regexp = re.compile( '\D*(?P<NUMBER>\dS)' )
	resonance = ''
	try:
		num = regexp.search( aFile ).group( 'NUMBER' )
		resonance = '#Upsilon('+num+')'
	except AttributeError:
		resonance = 'J#Psi'

	return resonance

if __name__ == '__main__':
	"""
	"""
        from optparse import OptionParser

        parser = OptionParser()
        parser.set_defaults(dim1Plots=False,dim2Plots=True)
        parser.add_option( '-i', '--input', action='store', dest='fileName', help='Input root file name, comma separated, no espaces' )
        parser.add_option( '-u', '--AllUpsilons', action='store_true', dest='allUpsilons', help='Make all upsilons comparations' )
        parser.add_option( '--dim1', action='store_true', dest='dim1Plots', help='Must I do 1-dim plots?' )
        parser.add_option( '--dim2', action='store_true', dest='dim2Plots', help='Must I do 2-dim plots?' )

        ( opt, args ) = parser.parse_args()

	if not opt.fileName:
		Message="""Missed mandatory argument -i FILENAME"""
		parser.error( Message )
	
	import pytnp
	import rootlogon

	if opt.allUpsilons:
		#--- We define only the fit_eff plots
		whatPlots = 'fit_eff'
		allFiles = opt.fileName
		allFiles = allFiles.split(',')
		if len(allFiles) != 3:
			Message = """I need 3 input files comma separated without espaces. I read this %s""" % opt.fileName
			parser.error( Message )
		
		resDict = {}
		resPlotDict = {}
		for aFile in allFiles:
			#--- Extract from the standard name file the resonance ---
			resonance = getResName( aFile )
			#---------------------------------------------------------
			#-- Create the pytnp object and the dict for the plots
			resDict[resonance] = pytnp.pytnp( aFile )
			resPlotDict[resonance] = {}
			#---- Making the plots for this resonance
			for name,rooPlot in resDict[resonance].RooPlot.iteritems():
				if name.find(whatPlots) != -1 and name.find('mcTrue') == -1:
					resPlotDict[resonance][name] = plotEff1D(rooPlot, name, resonance )
			exit()

	
	#TODO: poner en el titulo que rango estamos utilizando
	#      y que probes
	if opt.dim1Plots:
		tnp = pytnp.pytnp(opt.fileName)
		for name,rootPlot in tnp.RooPlot.iteritems():
			#Cuidado si no damos nombre machacara
			plotEff1D(rootPlot,name)
		del tnp

	if opt.dim2Plots:
		tnp = pytnp.pytnp(opt.fileName)
		resonance = ''
		for name,dataSet in tnp.RooDataSet.iteritems():
			plotEff2D(dataSet,resonance,name)
			exit()
		del tnp
	



