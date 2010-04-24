#!/usr/bin/env python
"""
"""
import ROOT

def inferInfo( name ):
	"""
	"""
	info = name.split('/')
	toReturn = ''
	if len(info) != 1:
		toReturn = info[1].split('_')[0]
		if info[0] == 'histoMuFromTk':
			toReturn += ' MuonID'
		elif info[0] == 'histoTrigger':
			### There is no underscore, change it in tnp Producer
			### Neither if is Global or tracker
			toReturn = info[1].split('pt')[0]
			toReturn += ' Trigger'

	return toReturn

def plotEff1D(rooPlot, namePlot, resonance):
	"""
	plotEff1D(ROOT.RooPlot, namePlot, resonance) -> ROOT.RooHist

	Given a ROOT.RooPlot object, name for the plot (without extension),
	and the name in latex format, the function creates a 1-dim plot 
	extracted from the object and it will save it in a eps file. 
	Also, the function returns the 	ROOT.RooHist contained in 
	the ROOT.RooPlot object.
	"""
	#--- Title from namePlot: namePlot must be 
	#--- in standard directory-like name
	title = resonance+' '+inferInfo(namePlot)
	#FIXME: Flexibilidad para entrar variables de entrada
	name = namePlot
	if namePlot == '':
	  	print """Error: you must introduce a name for the plot"""
		print plotEff1D.__doc__
		raise AttributeError
	
	#-- Plotted variable
	var = rooPlot.getPlotVar()
	#--- Graph, getHist returns a RooHist which inherits from
	#--- TGraphErrorAsym
	h = rooPlot.getHist()
	ymin = h.GetYaxis().GetBinLowEdge(1) #Solo tiene un bin?
	if ymin < 0:
		ymin = 0
	ymax = h.GetYaxis().GetBinUpEdge( h.GetYaxis().GetNbins() )
	print ymax
	xmin = h.GetXaxis().GetBinLowEdge(1) #Solo tiene un bin, es un TGraph
	xmax = h.GetXaxis().GetBinUpEdge( h.GetXaxis().GetNbins() )
	#Make canvas
	for isLog in [ ('',0) ]:#,('_log',1) ]:
		c = ROOT.TCanvas()
		if isLog[0] == 1:
			ymin = 1e-5
		c.SetLogy( isLog[1] )
		frame = c.DrawFrame(xmin,ymin,xmax,ymax)
		# Preparing to plot, setting variables, etc..
		frame.SetTitle( title )
		xlabel = var.getTitle()
		varUnit = var.getUnit()
		if varUnit != '':
			xlabel += '('+varUnit+')'
		frame.GetXaxis().SetTitle( xlabel.Data() ) #xlable is TString
		frame.GetYaxis().SetTitle( 'Efficiency' )
		h.Draw('P')
		plotName = name.replace('/','_')+isLog[0]+'.eps'
		c.SaveAs(plotName)
		c.Close()
		del c

	return h

def getBinning( var ):
	"""
	"""

	binsN = var.numBins()
	#binning = ROOT.RooBinning()
	binning = var.getBinning()
	arrayBins = binning.array()

	return binsN, arrayBins

def plotEff2D(dataSet, resonance, namePlot=''):
	"""
	"""
	#FIXME: Flexibilidad para entrar variables de entrada
	#FIXME: Cosmetics
	#FIXME: Meter los errores en la misma linea (ahora te salta
	#       de linea (TEXT option)
	if namePlot == '':
	  	print """Error: you must introduce a name for the plot"""
		print plotEff1D.__doc__
		raise AttributeError
	name = namePlot
	title = name+' '+inferInfo(name)+' '+dataSet.GetTitle()
	argSet = dataSet.get()
  	pt = argSet['pt'];
        eta = argSet['eta'];
        eff = argSet['efficiency'];
	# Este metodo no me gusta... lo hago a mana
	#h = dataSet.createHistogram(eta, pt)
	##### Creacion histograma
	##-- Bineado 
	ptNbins, arrayBinsPt = getBinning( pt )
	etaNbins, arrayBinsEta = getBinning( eta )
	h = ROOT.TH2F( 'h', '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
	#h.SetTitle( title )
	#h = ROOT.TH2F( 'h', '', ptNbins, arrayBinsPt, etaNbins, arrayBinsEta )
  	hlo = h.Clone("eff_lo")
  	hhi = h.Clone("eff_hi")
	
	print h.GetNbinsX(), h.GetNbinsY()
	for i in xrange(dataSet.numEntries()):
		_dummy = dataSet.get(i)
		b = h.FindBin(eta.getVal(), pt.getVal())
	#	print 'bin=',b,' pt =', pt.getVal(),' eta=',eta.getVal()
		h.SetBinContent(b, eff.getVal())
		h.SetBinError(b, eff.getErrorLo())
		hlo.SetBinContent(b, eff.getVal()+eff.getErrorLo())
    		hhi.SetBinContent(b, eff.getVal()+eff.getErrorHi())
	#Si es plot --> Entra un histo, graph o lo que sea, de momento
	#Lo dejo asi, pero hay que cambiarlo
	for isLog in [ ('',0), ('_log',1) ]:
		c = ROOT.TCanvas()
		c.SetLogy(isLog[1]) 
		h.GetYaxis().SetTitle('p_{t} (GeV/c)')
		h.GetXaxis().SetTitle('#eta')
		h.GetZaxis().SetTitle('eff')
		h.SetTitle( title )
		h.Draw('COLZ')
		htext = h.Clone('htext')
		htext.SetMarkerSize(1.0)
		htext.SetMarkerColor(1)
		if isLog[1]:
			ROOT.gStyle.SetPaintTextFormat("1.2f")
			htext.Draw('ESAMETEXT0')
		else:
			ROOT.gStyle.SetPaintTextFormat("1.3f")
			htext.Draw('SAMETEXT0')
		#-- Taking the extra symbols away...
		resonance = resonance.strip('#)')
		resonance = resonance.split('(')[0]
		plotName = resonance+name.replace('/','_')+isLog[0]+'.eps'
		print plotName
		c.SaveAs(plotName)
	#fout = ROOT.TFile('kkk.root','UPDATE')
	#fout.cd()
	#h.Write(name+'_efficiency')
	#hlo.Write(name+'_eff_low')
	#hhi.Write(name+'_eff_high')
	#fout.Close()
	#return c

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
	



