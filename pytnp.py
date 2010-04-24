"""
"""
import ROOT

#--- TODO: vale la pena que herede de un diccionario??
#--------- Se podira crear la llave del diccionario que
# es el propio objeto dinamicamente, i.e que vaya cambiando
# las llaves segun estemos en un directorio o en otro...
import sys

class pytnp(dict):
	"""
	Class to retrieve and encapsulate the 'tag and probe' 
	root file generated with the fit step of the TagAndProbe
	package from CMSSW.
	"""
	counter = 0
	__fileroot__ = None
	def __init__(self, filerootName, regexp = ''):
		"""
                pytnp(fileroota,regexp) -> pytnp object instance

		Create a dictionary with keys are the name of 
		the complete 'path' in a ROOT file of a ROOT.RooDataSet,
		and the values are the ROOT.RooDataSet itself.
		If 'regexp' is included, it will only be mapped
		the ROOT.RooDataSet matching with 'regexp'.
		The instance will contain the follow datamembers:
		   TCanvas, RooDataSet, RooPlot, RooFitResults
		which again are dictionaries analogous of the 
		instance itself.
		"""
		print 'Extracting info from '+filerootName+'.',
		sys.stdout.flush()
		classNames = ['TCanvas','RooDataSet','RooPlot','RooFitResult']
		fileroot = ROOT.TFile(filerootName)
		#self.__rootfile__ = fileroot
		#__dict__ 
		self.__dict__ = {}
		self.__dict__ = self.__extract__(fileroot, self.__dict__, regexp) 
		print ''
		self.__fileroot__ = fileroot
		#--- Instantiate the dict object
		for name, object in self.__dict__['RooDataSet'].iteritems():
			self[name] = object
		#Diccionario de directorios---> Espero a Luis
		#objectList = { }
		#-- Estructura de directorios: Parejas path-posicion total en 0/1/2/3..
	#	directories = set()
	#	for pathValDict in self.__dict__.itervalues():
	#		for dirNames in pathValDict.iterkeys():
	#			dirNames = dirNames.split('/')
	#			#dirNames.reverse()
	#			#Guardo el nombre del dir, el padre y el hijo
	#			#Si no tiene hijo guardamos None. El padre del top directory es tambien None
	#			directories.add( (dirNames[0],None,dirNames[1]) )
	#			for i in xrange(len(1,dirNames)-i):
	#				try:
	#					directories.add( (dirNames[i],dirNames[i-1],dirNames[i+1]) )
	#				except IndexError:
	#					directories.add( (dirNames[i],dirNames[i-1],None) )
	#	#pasa a lista
	#	refdirList = list( directories )
	#	# Y finalmente a diccionario
	#	for name,father,child in refdirList:
	#		if father is None and child is not None:
	#			self.__setattr__(name,child)
	#		elif child is not None:
	#			seff.__setattr__(name,child)
	#		elif child is None:
	#			#Get all the path
	#			grandfather 
	#			self._setattr__(name, self.__dict__[name]
	#			#		self.__DIR__ = dict( directories )
	#	#Creacion de los atributos (dinamicamente)--> 
	#	for i in obj.iterkeys():
	#	#	self.__setattr__(name,self.__dict__[name])
	#		#Diccionario: las keys son los elementos y los valores el tipo de objeto
	#	#	self[name]=classType
	#

	#def __getattribute__(self,name):
	#	"""
	#	"""
	#	try:
	#		#Controla los atributos definidos como TLeaf's
	#		#Para devolver el contenido del leaf
	#		if  self[name] == 'UInt_t':
	#			return self.__getattr__(name)
	#		else:
	#			return dict.__getattribute__(self,name)
	#	except KeyError:
	#		return dict.__getattribute__(self,name)

	#def __getattr__(self,name):
	#	"""
	#	"""
	#	try:
	#		#Devuelve el contenido del leaf
	#		return self.__dict__[name].GetValue()
	#	except:
	#		raise AttributeError, name

	def __extract__(self, Dir, dictObjects, regexp):
	 	"""
	 	__extract__(ROOT.TDirectory Dir, python dict, regexp) -> dict
	 	
		Recursive function to extract from a 'tag and probe' ROOT file all
		the relevant information. Returning a dictionary which stores all TCanvas,
		RooFitResult, RooDataSet and RooPlot with matches with regexp:
		{ 'TCanvas': 
		            {'directory/subdirectory/.../nameOfTCanvas' : <ROOT.TCanvas object>,
			     ...
			     },
		  'RooFitResult' : 
		            { 'directory/subdirectory/.../nameOfRooFitResult': <ROOT.RooFitResult object>,
			     ...
			     },
	 	  'RooDataSet':
		            { 'directory/subdirectory/.../nameOfRooDataSet': <ROOT.RooDataSet object>,
			     ...
			     },
	 	  'RooPlot':
		            { 'directory/subdirectory/.../nameOfRooPlot': <ROOT.RooPlot object>,
			     ...
			     }
		}
		            
	 	"""
		if pytnp.counter%100 == 0:
			print '.',
			sys.stdout.flush()
		# FIXED-------------------------------------------------
	 	#_dirSave = ROOT.gDirectory
	 	#Python --> _dirSave is a reference to ROOT.gDirectory, 
		#           so whenever gDirectory changes, _dirSaves 
		#           changes too. I can't use the gDirectory
		#-------------------------------------------------------
	 	_dirSave = Dir
		#Storing the father->child info
	 	for key in Dir.GetListOfKeys():
	 		className = key.GetClassName()
	 		if key.IsFolder():
	 			##-- Extracting the Folder from Dir
	 			_subdir = Dir.Get(key.GetName())
	 			##-- And browsing inside recursively
				pytnp.counter += 1
	 			dictObjects = self.__extract__(_subdir,dictObjects,regexp)
	 			##-- To avoid segmentation faults, we need to return
				##   at the original directory in order to continue
				##   extracting subdirectories (or elements of the directory)
	 			_dirSave.cd()
	 		##-- Storing in the dictionary the interesting objects
	 		elif className == 'TCanvas' or className == 'RooFitResult' or className == 'RooDataSet' or \
	 				className == 'RooPlot':
				# DEBUG ---------------------------
			        #print Dir.GetPath().split(':/')[1] #--- TO BE SKIPPED
				#----------------------------------
				pytnp.counter += 1
				#--Skipping if not match (Note that anything.find('') gives 0
				if (Dir.GetPath()+key.GetName()).find(regexp) == -1:
					continue
				try:
					#Asuming unique id object-->complet path
					dictObjects[className][Dir.GetPath().split(':/')[1]+'/'+key.GetName()] = Dir.Get(key.GetName())
				except KeyError:
					dictObjects[className] = { Dir.GetPath().split(':/')[1]+'/'+key.GetName(): Dir.Get(key.GetName()) }
	 
	 	return dictObjects

	def ls(self, className):
		"""
		ls( className ) 

		Print the identification of all the objects of type 'className'		
		"""
		message = '='*20+' '+className+' '+'='*20+'\n'
		try:
			for name in self.__getattribute__(className).iterkeys():
				message += name+'\n'
		except AttributeError:
			message = """
There's no class named %s!
                        """ % className

		print message

	def tableEff(self,name):
		"""
		tableEff( name ) 

		Print a table with the values of efficiencies.
		"""
		try:
			dataSet = self.RooDataSet[name]
			argSet = dataSet.get()
			pt = argSet['pt']
			eta= argSet['eta']
			eff = argSet['efficiency']
			for i in xrange(dataSet.numEntries()):
				dataSet.get(i)
				print 'pt=',pt.getVal(),' eta=',eta.getVal(),' eff=', eff.getVal()

		except KeyError:
			print 'THere is no RooDataSet named '+name+' in the file '+self.__fileroot__.GetName()
			raise KeyError

	### TODO: Esto puede hacerse en tiempo de construccion
	###       creando un dict, tuple, etc que acceda a esta
	###       info
	def inferInfo( self, name ):
		"""
		inferInfo( name ) -> str

		Giving a standard directory-like name of an object,
		the function returns what kind of efficiency is,
		MuonID or Trigger.
		"""
		info = name.split('/')
		toReturn = ''
		if len(info) != 1:
			toReturn = info[1].split('_')[0]
			if info[0] == 'histoMuFromTk':
				toReturn += ' MuonID'
			elif info[0] == 'histoTrigger':
				### ---- FIXED---------------------------------------
				### There is no underscore, change it in tnp Producer
				### Neither if is Global or tracker
				#toReturn = info[1].split('pt')[0]
				### -------------------------------------------------
				toReturn += ' Trigger'
	
		return toReturn


	def plotEff1D( self, rooPlot, namePlot, resonance, mustReturn = False ):
		"""
		plotEff1D(ROOT.RooPlot, namePlot, resonance, mustReturn = False) -> ROOT.RooHist
	
		Given a ROOT.RooPlot object, name for the plot (without extension),
		and the name in latex format, the function creates a 1-dim plot 
		extracted from the object and it will save it in a eps file. 
		Also, the function returns the ROOT.RooHist contained in 
		the ROOT.RooPlot object if mustReturn is True.
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
		c = ROOT.TCanvas()
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

		if mustReturn:
			return h


	def getBinning( self, var ):
		"""
		getBinning( ROOT.RooArgVar ) -> bins, arrayBins

		Giving a RooArgVar, the function returns 
		how many bins the variable has and an array
		with with his values.
		"""
	
		binsN = var.numBins()
		binning = var.getBinning()
		arrayBins = binning.array()
	
		return binsN, arrayBins
	
	def plotEff2D( self, dataSet, resonance, namePlot=''):
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
		
