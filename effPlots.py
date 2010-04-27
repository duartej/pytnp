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
		resonance = 'Upsilon'+num
	except AttributeError:
		if aFile.find( 'JPsi' ) != -1:
			resonance = 'JPsi'
		elif aFile.find( 'Upsilon' ) != -1:
			resonance = 'AllUpsilons'
	except:
		return None

	return resonance

if __name__ == '__main__':
	"""
	"""
        from optparse import OptionParser

        parser = OptionParser()
	#parser.set_defaults(dim1Plots=False,dim2Plots=True)
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
		if len(allFiles) < 2:
			Message = """I need at least 2 input files comma separated without espaces. I read this %s""" % opt.fileName
			parser.error( Message )
		#-- Dictionary of pytnp instance for every resonance
		tnpDict = {}
		#-- List of resonance we have
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
       Resonance_histo[MuFromTrk|Trigger]_....rot""" % aFile
       				exit()
			#---------------------------------------------------------
			#-- Create the pytnp instance
			tnpDict[resName] = pytnp.pytnp( aFile, whatPlots )
			resonance[ resName ] = tnpDict[resName].resLatex
			#---- Making the plots for this resonance
			for name,rooPlot in tnpDict[resName].RooPlot.iteritems():
				#--- Don't plot mcTrue information
				if name.find('mcTrue') == -1:
					#-- Store the name of the histos
					histoSet.add( name )
					#-- Storing and plotting
					tnpDict[resName].plotEff1D( name )
		#--- Plots for the all resonances
		#-- Assuming we have the same names for histos in every
		#   dict, but the first word (resonance dependent).
		for histo in histoSet:			
			c = ROOT.TCanvas()
			leg = ROOT.TLegend(0.6,0.25,0.8,0.4)
			inSame = '' 
			#-- How much resonances? To save the plot..
			howMuchRes = ''
			hMRLatex = ''
			hframe = None
			color = [ 1, 38, 46, 28, 30 ] 
			title = ''
			i = 0
			for resName,resLatex in resonance.iteritems():
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

	
	#TODO: poner en el titulo que rango estamos utilizando
	#      y que probes
	if opt.dim1Plots and not opt.allUpsilons:
		whatPlots = 'fit_eff'
		tnp = pytnp.pytnp(opt.fileName, whatPlots)
		resonance = tnp.resLatex
		for name,rootPlot in tnp.RooPlot.iteritems():
			if name.find('mcTrue') == -1:
				tnp.plotEff1D(name)
		del tnp

	if opt.dim2Plots:
		whatPlots = 'fit_eff'
		tnp = pytnp.pytnp(opt.fileName, whatPlots)
		resonance = tnp.resLatex
		for name,dataSet in tnp.RooDataSet.iteritems():
			if name.find('mcTrue') == -1:
				tnp.plotEff2D(name)
		del tnp
	



