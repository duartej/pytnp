"""
"""
import ROOT
import sys

class pytnp(dict):
	"""
	Class to retrieve and encapsulate the 'tag and probe' 
	root file generated with the fit step of the TagAndProbe
	package from CMSSW.
	"""
	#-- Name of the resonance
	resonance = None
	resLatex = None
	#-- Ranges of the variables ploted
	#variables = {}
	counter = 0
	#-- ROOT.TFile
	__fileroot__ = None
	def __init__(self, filerootName, regexp = ''):
		"""
                pytnp(fileroota,regexp) -> pytnp object instance

		Create a dictionary which are going to be populate
		with the plots and datasets already contained in the
		file and created a posterior.
		If 'regexp' is included, it will only  map 
		the objectstmatching with 'regexp'.
		The instance will contain the follow datamembers:
		    
		    TCanvas, RooDataSet, RooPlot, RooFitResults

		which again are dictionaries analogous of the 
		instance itself and can be extracted as datamembers.
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
		for name, dataSet in self.__dict__['RooDataSet'].iteritems():
			self[name] = dataSet
		#-- Get the resonances names
		self.resonance, self.resLatex = self.getResName( filerootName )
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
	
	def getResName( self, aFile ):
		"""
		getLatexRes( fileName ) -> str,str (latex)

		Extract from the file name the resonance
		and returns it plain and in Latex format.
		
		Warning: This function is highly dependent
		of the name of the file-- 
		Standard Format:  NameOFResonance_X_bala
		"""
		import re
	
		regexp = re.compile( '\D*(?P<NUMBER>\dS)' ) 
		resonance = ''
		resLatex = ''
		try:
			num = regexp.search( aFile ).group( 'NUMBER' )
			resonanceLatex = '#Upsilon('+num+')'
			resonance = 'Upsilon'+num

		except AttributeError:
			## Changed: we need to capture the AllUpsilon
			if aFile.find( 'JPsi' ) != -1:
				resonanceLatex = 'J/#Psi'
				resonance = 'JPsi'
			elif aFile.find( 'Upsilon' ) != -1:
				resonanceLatex =  'All #Upsilon'
				resonance = 'AllUpsilons'
		except:
			return None
	
		return resonance,resonanceLatex
	
	#TODO
	def write(self, fileOut):
		"""
		write( fileOut ) 

		Create a root file with all the contents of 
		the instance.
		"""
		pass

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

	def searchRange( self, name ):
		"""
		searchRange(name) -> 'range'

		Getting a directory-like name of a RooPlot
		extracts which's the range of the hidden 
		variable. It uses the directory-like notation
		to find which datased was used to generate the
		plot:
		RooPlot    -->  histoMuFromTk/Glb_pt_eta_mcTrue/fit_eff_plots/eta_plot__pt_bin10__mcTrue_true
		RooDataSet -->  histoMuFromTk/Glb_pt_eta_mcTrue/fit_eff
		"""
		#-- Getting the dataset name
		sName = name.split('_plots/')
		dataSet = None
		try:
			dataSet = self.RooDataSet[ sName[0] ]
		except KeyError:
			message = """
ERROR: What the f***!! This is an expected error... Exiting
                        """
			exit()
		#-- var1_plot__var2_binX[__something_else]
		#-- var1 is the plotted variable, var2 is the hidden
		#   variable and could be something labels, but doesn't
		#   matter to us
		Var = sName[1].split('__')
		plotVar = Var[0].split('_plot')
		hidVar = Var[1].split('_')[0]
		nBin = int(Var[1].split('_bin')[1])
		######---Hay otra forma mas facil: 
		#hidVar = self.RootPlot[name].GetTitle()
		# Devuelve 'variable_binX'
		argSet = dataSet.get()
		# FIXME
		#-- WARNING! If hidVar doesn't exist
		#   the program will crash when trying
		#   to retrieve the variable. I can't
		#   found a secure method to extract it.
		v = argSet[hidVar]
		bins, arrayBins = self.getBinning( v )
		rangeStr = hidVar+' range '
		rangeStr += '('+str(arrayBins[nBin])+','+str(arrayBins[nBin+1])+')'

		return rangeStr
		

	def plotEff1D( self, name ):
		"""
		plotEff1D( namePlot) -> ROOT.RooHist
	
		Given a name directory-like for a ROOT.RooPlot object,
	 	the function creates a 1-dim plot etracted from the
		object and it will save it in a eps file. Also
		it will store in the dictionary of the instance if
		the object does not exist.
		"""
                #-- Name for the histo and for to save the plot
		histoName = name
		#-- Checking if the object exists
		if self.has_key(histoName):
			# So, skipping the action.. it's done
			return None
		#--- Title from name: name must be 
		#--- in standard directory-like name
		title = self.resLatex+' '+self.inferInfo(name)+', '+self.searchRange(name)
		#FIXME: Flexibilidad para entrar variables de entradaa
		rooPlot = None
		try:
			rooPlot = self.RooPlot[name]
		except KeyError:
		  	print """Error: you must introduce a valid name"""
			print plotEff1D.__doc__ # OJO ESTO, esta sin comprobar
			raise KeyError
		
		#-- Plotted variable
		var = rooPlot.getPlotVar()
		#--- Graph, getHist returns a RooHist which inherits from
		#--- TGraphErrorAsym
		h = rooPlot.getHist()
		ymin = h.GetYaxis().GetBinLowEdge(1) #Solo tiene un bin?
		if ymin < 0:
			ymin = 0
		ymax = h.GetYaxis().GetBinUpEdge( h.GetYaxis().GetNbins() )
		xmin = h.GetXaxis().GetBinLowEdge(1) #Solo tiene un bin, es un TGraph
		xmax = h.GetXaxis().GetBinUpEdge( h.GetXaxis().GetNbins() )
		#Make canvas
		c = ROOT.TCanvas()
		frame = c.DrawFrame(xmin,ymin,xmax,ymax)
		# Preparing to plot, setting variables, etc..
		frame.SetTitle( title )
		h.SetTitle( title )  #To Store the info
		xlabel = var.getTitle()
		varUnit = var.getUnit()
		if varUnit != '':
			xlabel += '('+varUnit+')'
		frame.GetXaxis().SetTitle( xlabel.Data() ) #xlable is TString
		h.GetXaxis().SetTitle( xlabel.Data() )
		frame.GetYaxis().SetTitle( 'Efficiency' )
		h.GetYaxis().SetTitle( 'Efficiency' )
		h.Draw('P')
		c.SaveAs(self.resonance+'_'+histoName.replace('/','_')+'.eps')
		c.Close()
		del c
		#--- Storing the histo
		self[histoName] = h



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
	
	def plotEff2D( self, name ):
		"""
		plotEff2D( name ) 

		Giving a RooDataSet name in directory-like format,
		the function will do a bi-dimensional plot of 
		efficiency with pt and eta variables. Also, it
		will stores in the object instance
		"""
		#TODO: Flexibilidad para entrar variables de entrada
		#FIXME: Meter los errores en la misma linea (ahora te salta
		#       de linea (TEXT option)
		try:
			dataSet = self.RooDataSet[name]
		except KeyError:
		  	print """Error: you must introduce a valid name"""
			print plotEff2D.__doc__
			raise KeyError
		#--- Name for the histo and for the plot file to be saved
		histoName = 'TH2F_'+name
		#--- Checking if the histo is already stored and plotted
		if self.has_key(histoName):
			#-- Skipping, work it's done!
			return None
		#--- Title for the plot file
		title = self.resLatex+' '+self.inferInfo(name)+' '+dataSet.GetTitle()
		argSet = dataSet.get()
	  	pt = argSet['pt'];
	        eta = argSet['eta'];
	        eff = argSet['efficiency'];
		# Este metodo no me gusta... lo hago a mana
		#h = dataSet.createHistogram(eta, pt)
		##### Creacion histograma
		##-- Bineado 
		ptNbins, arrayBinsPt = self.getBinning( pt )
		etaNbins, arrayBinsEta = self.getBinning( eta )
		#-- To avoid warning in pyROOT
		hTitleOfHist = 'h'+name.replace('/','_')
		h = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
		#h.SetTitle( title )
		#h = ROOT.TH2F( 'h', '', ptNbins, arrayBinsPt, etaNbins, arrayBinsEta )
	  	hlo = h.Clone("eff_lo")
	  	hhi = h.Clone("eff_hi")
		
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
			plotName = self.resonance+'_'+name.replace('/','_')+isLog[0]+'.eps'
			c.SaveAs(plotName)
		#-- Storing the histo
		self[histoName] = h


