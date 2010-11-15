"""
Wrapper to ROOT objects (THwF, Graph, ...)
"""

from pytnp.libPytnp.management import printError,printWarning


#-- Auxiliary class to store attributes and useful info for the
#   plots
class auxK():
	""".. class:: auxK() 
	
	Auxiliary class used to store useful information for 
	the graphs functions. Makes use of the ``setkeywords``
	function to modify the 	its attributes. Per default::
	  
	  returnGraph = False
	  graphname = 'graph_'
	  rangeFrame = []
	  title = ''
	  markercolor = 1
	  markerstyle = 20
	  logX = False
	  logY = False
	  canvas = None
	"""
	returnGraph = False
	graphname = 'graph_'
	rangeFrame = []
	title = ''
	markercolor = 1
	markerstyle = 20
	logX = False
	logY = False
	canvas = None

def setkeywords( keywords, keyw ):
	""".. function setkeywords( keyword, keyw ) -> keyw

	:param keywords: dictionary containing the attributes and its values
	:type keywords: dict
	:param keyw: instance of auxK class
	:type keyw: auxK
	:return: an instance of auxK with its attributes modified with the ``keywords`` values
	:rtype: auxK

	:raise KeyError: If ``keywords`` contains a key which is not defined as attribute of ``auxK``
	"""
	#-- Sanity check
	VALID_KEYWORDS = [ _name for _name in dir( keyw ) if _name.find('__') == -1 ]
	for name, value in keywords.iteritems():
		if not name in VALID_KEYWORDS:
			message = "Invalid keyword argument '%s'\nValid keywords are '%s'" % (name, str(VALID_KEYWORDS))
			printError( setkeywords.__module__+'.'+setkeywords.__name__, message, KeyError )
		setattr( keyw, name, value )

	return keyw


def legend( posLeg ='CR' ):
	""".. function:: legend( pos='CR' ) -> leg

	Return a TLegend object positioned at 'pos'. The values
	admitted for 'pos' are::
	  
	  UL: Up-Left corner
	  UR: Up-Right corner
	  DL: Down-Left corner
	  DR: Down-Right corner
	  CR: Center-Right 

	:param pos: where positioning the legend (default: ``CR``)
	:type pos: string 
	:return: the object legend
	:rtype: ROOT.TLegend

	"""
	import ROOT

	if posLeg == 'UL':
		leg = ROOT.TLegend(0.2,0.69,0.4,0.79)
	elif posLeg == 'UR':
		leg = ROOT.TLegend(0.5,0.69,0.7,0.79)
	elif posLeg == 'DL':
		leg = ROOT.TLegend(0.2,0.41,0.4,0.51)
	elif posLeg == 'DR':
		leg = ROOT.TLegend(0.5,0.41,0.7,0.51)
	elif posLeg == 'CR':
		leg = ROOT.TLegend(0.5,0.29,0.70,0.39)
	else:
		mess = "Position '%s' not defined" % posLeg
		printError( legend.__module__+'.'+legeng.__name__, message, AttributeError )

	return leg

def paveText( title, posText='CR' ):
	""".. function:: paveText( pos='CR' ) -> pave

	Return a TLegend object positioned at 'pos'. The values
	admitted for 'pos' are::

	  UL: Up-Left corner
	  UR: Up-Right corner
	  DL: Down-Left corner
	  DR: Down-Right corner
	  CL: Center-Left
	  CR: Center-Right 
	  OG: Over the graphic
	
	:param pos: where positioning the legend (default: ``CR``)
	:type pos: string 
	:return: the object pave text
	:rtype: ROOT.TPaveText
	"""
	import ROOT

	if posText == 'UL':
		text = ROOT.TPaveText(0.25,0.8,0.45,0.9,"NDC")
	elif posText == 'UR':
		text = ROOT.TPaveText(0.55,0.8,0.75,0.9,"NDC")
	elif posText == 'DL':
		text = ROOT.TPaveText(0.25,0.1,0.45,0.3,"NDC")
	elif posText == 'DR':
		text = ROOT.TPaveText(0.55,0.1,0.75,0.3,"NDC")
	elif posText == 'CL':
		text = ROOT.TPaveText(0.25,0.4,0.45,0.6,"NDC")
	elif posText == 'CR':
		text = ROOT.TPaveText(0.55,0.4,0.75,0.6,"NDC")
	elif posText == 'OG':
		text = ROOT.TPaveText(0.45,0.93,0.65,0.98,"NDC")
	else:
		mess = "Position '%s' not defined" % posLeg
		printError( legend.__module__+'.'+legeng.__name__, message, AttributeError )

	text.AddText( title )
	text.SetBorderSize(0)
	text.SetFillColor(0)
	text.SetTextSize(0.04)
	text.SetFillStyle(4000)

	return text

def plotAsymGraphXY( X, Y, tx, ty, outputformat='eps', **keywords ):
	""".. function:: plotAsymGraphXY( X, Y, tx, ty, outputformat='eps'[, ...] )

	Creates a TGraphAsymmErrors plot and store

	:param X: x variable
	:type X: list of floats
	:param Y: y variable
	:type Y: list of floats
	:param tx: title of x-axis
	:type tx: string
	:param ty: title of y-axis
	:type ty: string
	:param outputformat: format to store the plot (default eps)
	:type outputformat: string
	:keyword keywords: anything contained in the auxK class
	:type keyword: dict
	"""
	import ROOT
	import rootlogon
	ROOT.gROOT.SetBatch( 1 )
	
	#-- Sanity check and get attributes keywords
	keyw = auxK()
	keyw = setkeywords( keywords, keyw )

        grafica = ROOT.TGraphAsymmErrors()
	#grafica.SetName( keyw.graphname )

        i = 0
	#-- Filling the graph
        for (x,xLo,xHi),(y,yLo,yHi) in zip( X, Y ):
                grafica.SetPoint( i, x, y )
		grafica.SetPointEXlow( i, x-xLo )
		grafica.SetPointEXhigh( i, xHi-x )
		grafica.SetPointEYlow( i, y-yLo )
		grafica.SetPointEYhigh( i, yHi-y )
                i += 1
	#-- If the user provided the canvas do not create
	frame = None
	if keyw.canvas:
		c = keyw.canvas
		frame = c.GetFrame()
	else:
		c = ROOT.TCanvas()

	if not frame:
		if len(keyw.rangeFrame) > 1:
			frame = c.DrawFrame( keyw.rangeFrame[0], keyw.rangeFrame[1], keyw.rangeFrame[2], keyw.rangeFrame[3] )
		else:
			Xval = map( lambda (x,xlo,xhi): x, X )
			Yval = map( lambda (x,xlo,xhi): x, Y )
			hX = ( max(Xval)-min(Xval) )*0.1
			hY = ( max(Yval)-min(Yval) )*0.1
			frame = c.DrawFrame( min(Xval)*(1.-hX), min(Yval)*(1.-hY), max(Xval)*(1.+hX), max(Yval)*(1+hY) )
		
		frame.GetXaxis().SetTitle( tx )
		#frame.GetXaxis().CenterTitle()
		frame.GetYaxis().SetTitle( ty )
		#frame.GetYaxis().CenterTitle()
		frame.SetTitle('')
		textTitle = paveText( keyw.title )
		textTitle.Draw()

        grafica.SetMarkerColor( keyw.markercolor )
        grafica.SetMarkerStyle( keyw.markerstyle )
        grafica.SetLineColor( keyw.markercolor )
        grafica.Draw('PSAME')

        if keyw.logX:
                c.SetLogx()
        if keyw.logY:
                c.SetLogy()

	if keyw.returnGraph:
		if not keyw.canvas:
			c.SaveAs( keyw.graphname+'.'+outputformat )
			c.Close()
		return grafica#, c  ---> Lo quiero o no, CUIDADO hay que propagarlo!!
	
	if not keyw.canvas:
		c.SaveAs( keyw.graphname+'.'+outputformat )
		c.Close()

	#return None, None

def plotMapTH2F( X,Y,Z, tx, ty, tz,  NbinsX, arrayX, NbinsY, arrayY, outputformat='eps', **keywords ):
	""".. function:: plotMapTH2F( X, Y, Z, tx, ty, tz, NbinsX, arrayX, NbinsY, arrayY, outputformat='eps'[, ...])

	Creates a TH2F plot using Z as values of the bins X,Y

	:param X: x variable
	:type X: list of floats
	:param Y: y variable
	:type Y: list of floats
	:param Z: z variable
	:type Z: list of floats
	:param tx: title of x-axis
	:type tx: string
	:param ty: title of y-axis
	:type ty: string
	:param tz: title of z-axis
	:type tz: string
	:param NbinsX: number of bins in x-axis
	:type NbinsX: int
	:param arrayX: double* C-like array containing the bins in x-axis 
	:type arrayX: array
	:param NbinsY: number of bins in y-axis
	:type NbinsY: int
	:param arrayY: double* C-like array containing the bins in y-axis 
	:type arrayY: array
	:param outputformat: format to store the plot (default eps)
	:type outputformat: string
	
	:keyword keywords: anything contained in the auxK class
	:type keyword: dict
	"""
	import ROOT
	import rootlogon
	ROOT.gROOT.SetBatch( 1 )
	#ROOT.gStyle.SetPadRightMargin(0.17)
	
	#-- Sanity check and get attributes keywords
	keyw = auxK()
	keyw = setkeywords( keywords, keyw )

	hist = ROOT.TH2F( keyw.graphname, keyw.graphname, NbinsX, arrayX, NbinsY, arrayY )

	if( len(keyw.rangeFrame) ) > 1:
		hist.GetZaxis().SetLimits( keyw.rangeFrame[0], keyw.rangeFrame[1] )
	else:
		Zval = map( lambda (x,xlo,xhi): x, Z )
		hZ = ( max(Zval)-min(Zval) )*0.1
		hist.GetZaxis().SetLimits( min(Zval)*(1.-hZ), max(Zval)*(1+hz) )

	for x, y, (z,zerror) in zip( X, Y, Z ):
		b = hist.FindBin( x, y )
		hist.SetBinContent( b, z )
		hist.SetBinError( b, zerror )

	c = ROOT.TCanvas()

	hist.SetMarkerSize( 1.0 )
	hist.SetMarkerStyle( keyw.markerstyle )
	hist.SetMarkerColor( keyw.markercolor )
	hist.GetXaxis().SetTitle( tx )
	#hist.GetXaxis().CenterTitle()
	hist.GetYaxis().SetTitle( ty )
	#hist.GetYaxis().CenterTitle()
	hist.SetZTitle( tz )
	hist.SetContour(50)
	hist.GetZaxis().SetLabelSize(0.02)
	
	hist.Draw( 'COLZ' )
	#-- Overimpress values and errors
	htext = hist.Clone('htext')
	htext.SetMarkerSize(1.0)
	htext.SetMarkerColor(1)
	ROOT.gStyle.SetPaintTextFormat("1.3f")
	if NbinsX+NbinsY < 7 :
		Tmarkersize =2.2
	else:
		Tmarkersize = 0.7
	htext.SetMarkerSize(Tmarkersize)
	htext.Draw("SAMETEXTE0")
	hist.SetTitle('')
	textTitle = paveText( keyw.title,'OG' )
	textTitle.Draw()#'SAME'

        c.SaveAs( keyw.graphname+'.'+outputformat )
        c.Close()

	return hist


