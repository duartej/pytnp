"""
Wrapper to ROOT objects (THwF, Graph, ...)
"""

from pytnp.libPytnp.management import printError,printWarning


#-- Auxiliary class to store attributes and useful info for the
#   plots
class auxK():
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
	"""
	"""
	#-- Sanity check
	VALID_KEYWORDS = [ _name for _name in dir( keyw ) if _name.find('__') == -1 ]
	for name, value in keywords.iteritems():
		if not name in VALID_KEYWORDS:
			message = "Invalid keyword argument '%s'\nValid keywords are '%s'" % (name, str(VALID_KEYWORDS))
			printError( plotGraphXY.__module__,'.'+plotGraphXY.__name__, message, KeyError )
		setattr( keyw, name, value )

	return keyw


def legend( posLeg ):
	"""
	legend( 'pos' ) --> TLegend

	Return a TLegend object positioned at 'pos'. The values
	admitted for 'pos' are::
	  
	  UL: Up-Left corner
	  UR: Up-Right corner
	  DL: Down-Left corner
	  DR: Down-Right corner

	"""
	import ROOT

	if posLeg == 'UL':
		leg = ROOT.TLegend(0.2,0.8,0.4,0.9)
	elif posLeg == 'UR':
		leg = ROOT.TLegend(0.5,0.8,0.9,0.9)
	elif posLeg == 'DL':
		leg = ROOT.TLegend(0.2,0.2,0.4,0.4)
	elif posLeg == 'DR':
		leg = ROOT.TLegend(0.7,0.2,0.9,0.4)
	else:
		mess = "Position '%s' not defined" % posLeg
		printError( legend.__module__+'.'+legeng.__name__, message, AttributeError )

	return leg

def paveText( title, posText='CR' ):
	"""
	paveText( 'pos' ) --> TPaveText

	Return a TLegend object positioned at 'pos'. The values
	admitted for 'pos' are::

	  UL: Up-Left corner
	  UR: Up-Right corner
	  DL: Down-Left corner
	  DR: Down-Right corner
	  CL: Center-Left
	  CR: Center-Right 
	  OG: Over the graphic
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
#logX='False', logY='False', valLine=[]):
	"""
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
	"""
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


#def plotGraphXY( X, Y, tx, ty, outputformat='eps', **keywords ):
##logX='False', logY='False', valLine=[]):
#	"""
#	"""
#	#-- Auxiliar class to deal with the keywords
#	class auxK():
#		returnGraph = False
#		graphname = 'graph'
#		rangeFrame = []
#		title = ''
#		markercolor = 1
#		markerstyle = 20
#		logX = False
#		logY = False
#
#	import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#	#-- Sanity check
#	keyw = auxK()
#	VALID_KEYWORDS = [ _name for _name in dir( keyw ) if _name.find('__') == -1 ]
#	for name, value in keywords:
#		if not name in VALID_KEYWORDS:
#			message = "Invalid keyword argument '%s'\nValid keywords are '%s'" % (name, str(VALID_KEYWORDS))
#			printError( plotGraphXY.__module__,'.'+plotGraphXY.__name__, message, KeyError )
#		setattr( keyw, name, value )
#
#        grafica = ROOT.TGraph()
#
#        i = 0
#	#-- Filling the graph
#        for x,y in zip( X, Y ):
#                grafica.SetPoint( i, x, y )
#                i += 1
#
#        c = ROOT.TCanvas()
#	if len(rangeFrame) > 1:
#		frame = c.DrawFrame( keyw.rangeFrame[0], keyw.rangeFrame[2], keyw.rangeFrame[1], keyw.rangeFrame[3] )
#	else:
#	        frame = c.DrawFrame( min(X)-1, min(Y)-1, max(X)+1, max(Y)+1 )
#
#        frame.GetXaxis().SetTitle( tx )
#        #frame.GetXaxis().CenterTitle()
#        frame.GetYaxis().SetTitle( ty )
#        #frame.GetYaxis().CenterTitle()
#	frame.SetTitle( keyw.title )
#
#        grafica.SetMarkerColor( keyw.markercolor )
#        grafica.SetMarkerStyle( keyw.markerstyle )
#        grafica.SetLineColor( keyw.markercolor )
#        grafica.Draw('PSAME')
#
#	#if len(valLine) > 1:
#	#	valXs = valLine[0]
#	#	valYs = valLine[1]
#	#	gLINE = ROOT.TGraph()
#	#	i = 0
#	#	for valX, valY in zip( valXs, valYs ):
#	#		gLINE.SetPoint( i, valX, valY )
#	#		i += 1
#
#	#	gLINE.SetLineColor( 12)
#	#	gLINE.SetLineStyle( 2 )
#	#	gLINE.SetLineWidth( 2)
#	#	gLINE.Draw( 'LSAME' )
#	
#        if keyw.logX:
#                c.SetLogx()
#        if keyw.logY:
#                c.SetLogy()
#
#	if keyw.returnGraph:
#		c.SaveAs( fileOut )
#		c.Close()
#		return grafica
#
#        c.SaveAs( keyw.graphname+'.'+outputformat )
#        c.Close()



	
#def plotXY2D( X, Y, X2, Y2, tx, ty, tl1, tl2, fileOut, rangeFrame=[], typeGraph='line', logX='False', logY='False', dreta='True'):
#        import ROOT
#        import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#        grafica = ROOT.TGraph()
#	g2 = ROOT.TGraph()
#
#        i = 0
#        for x,y in zip( X, Y ):
#                grafica.SetPoint( i, x, y )
#                i += 1
#	j = 0
#	for x,y in zip( X2, Y2):
#		g2.SetPoint( j, x, y )
#
#        c = ROOT.TCanvas()
#	if len(rangeFrame) > 1:
#		frame = c.DrawFrame( rangeFrame[0], rangeFrame[2], rangeFrame[1], rangeFrame[3] )
#	else:
#	        frame = c.DrawFrame( min(X)-1, min(Y)-1, max(X)+1, max(Y)+1 )
#
#        frame.GetXaxis().SetTitle( tx )
#        frame.GetXaxis().CenterTitle()
#        frame.GetYaxis().SetTitle( ty )
#        frame.GetYaxis().CenterTitle()
#
#        grafica.SetMarkerColor(9)
#        grafica.SetMarkerStyle(20)
#        grafica.SetMarkerSize(0.8)
#        grafica.Draw('P')
#
#	if typeGraph == 'points':
#		g2.SetMarkerColor( 8 )
#		g2.SetMarkerStyle( 22 )
#		g2.SetMarkerSize(0.8)
#		g2.Draw('PSAME')
#	elif typeGraph == 'line':
#		g2.SetLineColor( 1 )
#		g2.SetLineStyle( 1 )
#		g2.Draw('LSAME')
#
#	if dreta == 'True':
#		leg = ROOT.TLegend(0.6,0.8,0.9,0.9)
#	else:
#		leg = ROOT.TLegend(0.2,0.8,0.5,0.9)
#
#
#	leg.AddEntry( grafica, tl1, 'P' )
#	if typeGraph == 'line':
#		leg.AddEntry( g2, tl2, 'L' )
#	else:
#		leg.AddEntry( g2, tl2, 'P' )
#	leg.SetTextSize(0.04)
#        leg.Draw()
#	
#	if logX == 'True':
#		c.SetLogx()
#	if logY == 'True':
#		c.SetLogy()
#
#        c.SaveAs( fileOut )
#        c.Close()
#
#        return
#
#def plotXY4D( listX, listY, tx, ty, tl, fileOut, rangeFrame=[], posLeg='UR', logX='False', logY='False'):
#	"""
#	listX  =  [ vector X1, vector X2, vector X3, vector X4 ]
#	listY ::= it's the same
#	
#	listtl ::= list of legends
#	"""
#        import ROOT
#        import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#	X1 = listX[0]
#	X2 = listX[1]
#	X3 = listX[2]
#	X4 = listX[3]
#
#	Y1 = listY[0]
#	Y2 = listY[1]
#	Y3 = listY[2]
#	Y4 = listY[3]
#
#	g1 = ROOT.TGraph()
#	g2 = ROOT.TGraph()
#	g3 = ROOT.TGraph()
#	g4 = ROOT.TGraph()
#
#        i = 0
#        for x,y in zip( X1, Y1 ):
#                g1.SetPoint( i, x, y )
#                i += 1
#
#        i = 0
#        for x,y in zip( X2, Y2 ):
#                g2.SetPoint( i, x, y )
#                i += 1
#
#        i = 0
#        for x,y in zip( X3, Y3 ):
#                g3.SetPoint( i, x, y )
#                i += 1
#
#        i = 0
#        for x,y in zip( X4, Y4 ):
#                g4.SetPoint( i, x, y )
#                i += 1
#
#
#        c = ROOT.TCanvas()
#
#	if len(rangeFrame) > 1:
#		frame = c.DrawFrame( rangeFrame[0], rangeFrame[2], rangeFrame[1], rangeFrame[3] )
#	else:
#		minX = []
#		maxX = []
#		minY = []
#		maxY = []
#		for i in xrange(len(listX)):
#			minX.append( min(listX[i]) )
#			maxX.append( max(listX[i]) )
#			minY.append( min(listY[i]) )
#			maxY.append( max(listY[i]) )
#
#		frame = c.DrawFrame( min(minX)-1, min(minY)-1, max(maxX)+1, max(maxY)+1 )
#
#        frame.GetXaxis().SetTitle( tx )
#        frame.GetXaxis().CenterTitle()
#        frame.GetYaxis().SetTitle( ty )
#        frame.GetYaxis().CenterTitle()
#
#	_color = [2,1,9,8]
#	_style = [20,21,22,23]
#	
#        g1.SetMarkerColor( _color[0] )
#        g1.SetMarkerStyle( _style[0] )
#        g1.SetMarkerSize(0.7)
#        g1.Draw('P')
#	
#        g2.SetMarkerColor( _color[1] )
#        g2.SetMarkerStyle( _style[1] )
#        g2.SetMarkerSize(0.7)
#        g2.Draw('PSAME')
#
#        g3.SetMarkerColor( _color[2] )
#        g3.SetMarkerStyle( _style[2] )
#        g3.SetMarkerSize(0.7)
#        g3.Draw('PSAME')
#
#        g4.SetMarkerColor( _color[3] )
#        g4.SetMarkerStyle( _style[3] )
#        g4.SetMarkerSize(0.7)
#        g4.Draw('PSAME')
#
#	leg = legend( posLeg )
#
#	leg.AddEntry( g1, tl[0], 'P' )
#	leg.AddEntry( g2, tl[1], 'P' )
#	leg.AddEntry( g3, tl[2], 'P' )
#	leg.AddEntry( g4, tl[3], 'P' )
#	leg.SetTextSize(0.03)
#        leg.Draw()
#	
#	if logX == 'True':
#		c.SetLogx()
#	if logY == 'True':
#		c.SetLogy()
#
#        c.SaveAs( fileOut )
#        c.Close()
#
#        return
#
#
#def plotXYClass( X, Y, tx, ty, Class, tl1, tl2, fileOut, rangeFrame=[], logX='False', logY='False', dreta='True' ):
#        import ROOT
#        import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#        gAGN   = ROOT.TGraph()
#	gSBG   = ROOT.TGraph()
#
#	i = 0
#	j = 0
#        k = 0
#        for valx, valy, clase  in zip( X, Y, Class ):
#		if clase == '1':
#			gAGN.SetPoint( i, valx, valy )
#                        i += 1
#
#                elif clase == '0':
#			gSBG.SetPoint( j, valx, valy )
#                        j += 1
#		else:
#			k += 1
#
#	print "No se han clasificado ", k, " fuentes"
#
#        c = ROOT.TCanvas()
#	if len(rangeFrame) > 1:
#		frame = c.DrawFrame( rangeFrame[0], rangeFrame[2], rangeFrame[1], rangeFrame[3] )
#	else:
#        	frame = c.DrawFrame( min(X)-1, min(Y)-1, max(X)+1, max(Y)+1 )
#        frame.GetXaxis().SetTitle( tx )
#	frame.GetXaxis().CenterTitle()
#        frame.GetYaxis().SetTitle( ty )
#	frame.GetYaxis().CenterTitle()
#	
#	if dreta == 'True':
#		leg = ROOT.TLegend(0.6,0.8,0.9,0.9)
#	else:
#		leg = ROOT.TLegend(0.2,0.8,0.5,0.9)
#	leg.AddEntry( gAGN, tl1+' ('+str(i)+')' , 'P' )
#	leg.AddEntry( gSBG, tl2+' ('+str(j)+')' , 'P' )
#	leg.SetTextSize(0.04)
#        leg.Draw()
#
#        gAGN.SetMarkerColor(9)
#        gAGN.SetLineColor(9)
#        gAGN.SetMarkerStyle(22)
#        gAGN.SetMarkerSize(0.7)
#        gAGN.Draw('P')
#
#        gSBG.SetMarkerStyle(20)
#        gSBG.SetMarkerColor(46)
#        gSBG.SetLineColor(46)
#        gSBG.SetMarkerSize(0.7)
#        gSBG.Draw('PSAME')
#
#	if logX == 'True':
#		c.SetLogx()
#	if logY == 'True':
#		c.SetLogy()
#
#        c.SaveAs( fileOut )
#        c.Close()
#
#	return
#
#def plotXYErr( X, Y, eX, eY, tx, ty, fileOut, rangeFrame=[], logX='False', logY='False' ):
#        import ROOT
#        import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#        grafica = ROOT.TGraphErrors()
#
#        i = 0
#        for x,y,ex,ey in zip( X, Y, eX, eY ):
#                grafica.SetPoint( i, x, y )
#		grafica.SetPointError( i, ex, ey )
#                i += 1
#
#        c = ROOT.TCanvas()
#	if len(rangeFrame ) > 1:
#		frame = c.DrawFrame( rangeFrame[0], rangeFrame[2],rangeFrame[1], rangeFrame[3] )
#	else:
#		frame = c.DrawFrame( min(X), min(Y), max(X), max(Y) )
#	
#        frame.GetXaxis().SetTitle( tx )
#        frame.GetXaxis().CenterTitle()
#        frame.GetYaxis().SetTitle( ty )
#        frame.GetYaxis().CenterTitle()
#
#        grafica.SetMarkerColor(9)
#	grafica.SetLineColor(9)
#        grafica.SetMarkerStyle(20)
#        grafica.SetMarkerSize(1.0)
#        grafica.Draw('P')
#
#	if logX == 'True':
#        	c.SetLogx()
#	if logY == 'True':
#        	c.SetLogy()
#
#        c.SaveAs( fileOut )
#        c.Close()
#
#        return
#
#def THist1D( X, nbinsX, tx, fileOut, logX='False', logY='False', color=46, rangeL=[], Stat='F'):
#
#	import ROOT
#	import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#        c = ROOT.TCanvas()
#
#        hist = ROOT.TH1F('hh', '', nbinsX, min(X), max(X) )
#
#        for i in xrange( len(X) ):
#                hist.Fill( X[i] )
#
#	Xmin = min(X)
#	Xmax = max(X)
#
#	if len(rangeL) > 1:
#		x1 = rangeL[0]
#		x2 = rangeL[1]
#		y1 = rangeL[2]
#		yrange = rangeL[3]
#	else: 
#		x1 = int( Xmin ) - 0.15*int( Xmin )
#		x2 = int( Xmax ) + 0.15*int( Xmax )
#		y1 = 0
#		yrange = 1.2*int( hist.GetMaximum() )
#
#	hframe = c.DrawFrame( x1, y1, x2, yrange )
#	hframe.GetXaxis().SetTitle( tx )
#	hframe.GetXaxis().CenterTitle() 
#	hframe.Draw()
#
#        hist.SetLineColor( color )
#        hist.SetFillColor( color )
#        hist.SetFillStyle( 3017 )
#	hist.GetXaxis().SetTitle( tx )
#	hist.GetXaxis().CenterTitle()
#
#        hist.Draw('SAME')
#
#	if logX == 'True':
#		c.SetLogx()
#	if logY == 'True':
#		c.SetLogy()
#
#        c.SaveAs( fileOut )
#        c.Close()
#
#	if Stat == 'T':
#		PrintEstadisticos( fileOut+': '+tx, hist )
#
#        return
#
#
#def THist2DRange( X, nbinsX, tl1, Y, nbinsY, tl2, tx, fileOut, posLeg='UL', range=[], Norm='False', Stat='F' ):
#
#	import ROOT
#	import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#	c = ROOT.TCanvas()
#
#	Xmin  = min(X)
#	Xmax  = max(X)
#
#        Ymin  = min(Y)
#        Ymax  = max(Y)
#
#	title=''
#        histX = ROOT.TH1F('hh', title, nbinsX, Xmin, Xmax )
#        for i in xrange( len(X) ):
#                histX.Fill( X[i] )
#        
#	histY = ROOT.TH1F('hh', title, nbinsY, Ymin, Ymax )
#        for i in xrange( len(Y) ):
#                histY.Fill( Y[i] )
#
#        # Definimos LOS RANGOS DE LAS X's Y LAS Y's
#	if len(range) > 1:
#		x1 = range[0]
#		x2 = range[1]
#		y1 = range[2]
#		yrange = range[3]
#	else: 
#		#x1 = -1.0*( int( min( Xmin, Ymin ) - 2.0*min( Xmin, Ymin ) ) )
#		#x2 = int( max( Xmax, Ymax ) + 2.0*max( Xmax, Ymax ) )
#		x1 = min( Xmin, Ymin ) - 0.15*min( Xmin, Ymin )
#		x2 = max( Xmax, Ymax ) + 0.15*max( Xmax, Ymax )
#		y1 = 0
#		yrange = 1.2*int( max( histX.GetMaximum(), histY.GetMaximum()) )
#
#	hframe = c.DrawFrame( x1, y1, x2, yrange )
#	hframe.GetXaxis().SetTitle( tx )
#	hframe.GetXaxis().CenterTitle() 
#	hframe.Draw()
#
#	if Norm == 'True':
#		histX.SetNormFactor( 1 )
#		histY.SetNormFactor( 1 )
#		
#        histX.SetLineColor( 9 )
#        histX.SetFillColor( 9 )
#        histX.SetFillStyle( 3004 )
#	histX.Draw('SAME')
#
#        histY.SetLineColor( 12 )
#        histY.SetFillColor( 12 )
#        histY.SetFillStyle( 3005 )
#	histY.Draw('SAME')
#
#	leg = legend( posLeg )
#        leg.AddEntry( histX, tl1,'F' )
#        leg.AddEntry( histY, tl2, 'F' )
#	leg.SetTextSize(0.04)
#        leg.Draw('SAME')
#    
#	c.SaveAs( fileOut )
#        c.Close()
#
#	if Stat == 'T':
#		PrintEstadisticos( fileOut+': '+tl1, histX )
#		PrintEstadisticos( fileOut+': '+tl2, histY )
#
#	del histX
#	del histY
#	return
#
#def THist2DNorm( X, nbinsX, tl1, Y, nbinsY, tl2, tx, fileOut, limits='False', dreta='True', logX='False', logY='False' ):
#
#	import ROOT
#	import rootlogon
#	ROOT.gROOT.SetBatch( 1 )
#	
#	c = ROOT.TCanvas()
#
#	minx = min( min(X), min(Y) )
#	maxx = max( max(X), max(Y) )
#	nbins = max( nbinsX, nbinsY )
#	title=''
#
#	histX = ROOT.TH1F('hhX', title, nbinsX, min(X), max(X) )
#	histY = ROOT.TH1F('hhY', title, nbinsY, min(Y), max(Y) )
#	
#	#title=''
#        #histX = ROOT.TH1F('hhX', title, nbinsX+6, Xmin, Xmax )
#        for i in xrange( len(X) ):
#                histX.Fill( X[i] )
#
#	#histY = ROOT.TH1F('hhY', title, nbinsY+6, Ymin, Ymax )
#        for i in xrange( len(Y) ):
#                histY.Fill( Y[i] )
#
#        # Definimos LOS RANGOS DE LAS X's Y LAS Y's
#
#	histX.SetNormFactor( 1 )
#        histX.SetLineColor( 9 )
#        histX.SetFillColor( 9 )
#        histX.SetFillStyle( 3004 )
#
#	histY.SetNormFactor( 1 )
#        histY.SetLineColor( 12 )
#        histY.SetFillColor( 12 )
#        histY.SetFillStyle( 3005 )
#	
#	if (histX.GetMaximum())/sum(X) >= histY.GetMaximum()/sum(Y):
#		#histX.SetMaximum( histX.GetMaximum() + 1.5* histX.GetMaximum() )
#		histX.GetXaxis().SetTitle( tx )
#		histX.GetXaxis().CenterTitle()
#		histX.SetMaximum( float( histX.GetMaximum() ) + 0.5 * histX.GetMaximumBin() )
#		histX.SetAxisRange(minx, maxx, "X")
#		histX.Draw()
#		histY.Draw('SAME')
#	else:
#		#histY.SetMaximum( histY.GetMaximum() + 1.5 *  histY.GetMaximum() )
#		histY.GetXaxis().SetTitle( tx )
#		histY.GetXaxis().CenterTitle()
#		histY.SetMaximum( float( histY.GetMaximum() ) + 0.5 * histY.GetMaximumBin() )
#		histY.SetAxisRange(minx, maxx, "X")
#		histY.Draw()
#		histX.Draw('SAME')
#	
#	if dreta == 'True':
#		leg = ROOT.TLegend( 0.55,0.75,0.9,0.9 )
#	else:
#		leg = ROOT.TLegend( 0.2,0.75,0.4,0.9 )
#        leg.AddEntry( histX, tl1+' ('+str(len(X))+')','F' )
#        leg.AddEntry( histY, tl2+' ('+str(len(Y))+')', 'F' )
#	leg.SetTextSize(0.05)
#        leg.Draw('SAME')
#    
#	if logX == 'True':
#		c.SetLogx()
#	if logY == 'True':
#		c.SetLogy()
#
#	c.SaveAs( fileOut )
#        c.Close()
#
#	return
