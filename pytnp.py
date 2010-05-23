"""
"""
import ROOT
import sys

def getResName( aFile ):
	"""
	getResName( fileName ) -> str,str (latex)

	Extract from the file name the resonance
	and returns it plain and in Latex format.
	
	Warning: This function is highly dependent
	of the name of the file-- 
	Standard Format:  NameOFResonance_X_blabla
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
		elif aFile.find( 'Upsilon' ) != 0:
			resonanceLatex =  'All #Upsilon'
			resonance = 'AllUpsilons'
		elif aFile.find( 'Z' ) != -1:
			resonanceLatex = 'Z#rightarrow#mu#mu'
			resonance = 'Z'

		if aFile.find( 'DATA' ) != -1:
			resonanceLatex += ' Data'
			resonance += '_DATA'
	except:
		return None

	return resonance,resonanceLatex

#TODO: Puede hacerse con **keywords. pt=valor, eta=valor,...
def getEff( dataSet, pt, eta ):
	"""
	getEff(pt, eta) --> eff, effErrorLow, effErrorHigh, error

	Giving a pt and eta returns the efficiency which 
	corresponds to those values
	"""
	#-- Get the table of efficiencies
	tableList = tableEff( dataSet )
	for valDict in tableList:
		#-- Extract ranges
		ptRanges = valDict['pt'][1:]
		etaRanges = valDict['eta'][1:]
		if ( ptRanges[0] <= pt and ptRanges[1] >= pt ) and \
				( etaRanges[0] <= eta and etaRanges[1] >= eta ):
					return valDict['eff']
				
	print 'There is no bin where live the pair pt=',pt,', eta=',eta
	return None
				
def getBinning( var ):
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
	
def tableEff(dataSet):
	"""
	tableEff( dataSet ) --> tableList

	Giving a RooDataSet, the function returns a list where every 
	element is an entry of the RooDataSet stored as a dictionary:
	For every entry we have
	                { 'pt':  (pt, minimum pt bin, maximum pt bin),
	                  'eta': (eta, minimum eta bin, maximum eta bin),
			  'eff': (eff, error low, error high, error)
			}

	"""
	#TODO: usando el try, permitir tambien la busqueda para TH2
	try:
		argSet = dataSet.get()
		pt = argSet['pt']
		eta= argSet['eta']
		eff = argSet['efficiency']
		valList= []
		for i in xrange(dataSet.numEntries()):
			dataSet.get(i)
			#print 'pt=',pt.getVal(),' eta=',eta.getVal(),' eff=', eff.getVal()
			#Change: watch this! for pt and eta Hi and Lo is the limit of the bin
			#                    For efficiencies. is the asymmetric error?
			valList.append( { 'pt':(pt.getVal(), pt.getVal()+pt.getErrorLo(), pt.getVal()+pt.getErrorHi()),\
					'eta': (eta.getVal(), eta.getVal()+eta.getErrorLo(), eta.getVal()+eta.getErrorHi()),\
					'eff': (eff.getVal(), eff.getErrorLo(), eff.getErrorHi(), eff.getError() )
					}
				      )
		return valList
	except AttributeError:
		print dataSet+' is not a RooDataSet'
		raise AttributeError

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
	#-- Attribute dictionay##FIXME Es realmentee necesario?
	__attrDict__ = {}
	def __init__(self, filerootName, **keywords):
		"""
                pytnp(fileroota,...) -> pytnp object instance

		Create a dictionary which are going to be populate
		with the plots and datasets already contained in the
		file.
		If dataset is included, it will only  map 
		the object matching with 'dataset'.
		If resonance=(name,latexName) is included the filename is not necessary
		to be an standard tag and probe name (i.e. Resonance_blabla.root).
		If mcTrue is set to True it will store the mcTrue info
		and will associate each dataset with their mcTrue dataset.
		The instance will contain the follow datamembers:
		    
		    TCanvas, RooDataSet, RooPlot, RooFitResults

		which again are dictionaries analogous of the 
		instance itself and can be extracted as datamembers.
		"""
		#--- Checking the keys dictionary passed ----#
		#--- Keys valid
		valid_keys = ['resonance', 'dataset','mcTrue']
		#---- Some initializations
		dataset = ''
		for i in keywords.keys():
			if not i in valid_keys:
				message ='\033[1;31mpytnp: invalid instance of pytnp: you can not use %s as key argument, ' % i
				message += ' key arguments valids are \'resonance\', \'dataset\', \'mcTrue\' \033[1;m' 
				raise IOError, message
			#---Checking the correct format and storing
			#---the names provided by the user
			elif i == 'resonance':
				message ='\033[1;31mpytnp: Not valid resonance=%s; resonance key must be a tuple containing (\'name\',\'nameInLatex\')\033[1;m' \
						% str(keywords['resonance'])
				if len(keywords['resonance']) != 2:
					print message
					raise KeyError
				else:
					if keywords['resonance'][0].find('#') != -1 \
							or keywords['resonance'][0].find('{') != -1  :
						print message		
						raise KeyError
					#--- Storing resonance provided by user
					self.resonance = keywords['resonance'][0]
					self.resLatex  = keywords['resonance'][1]
			elif i == 'dataset':
				dataset = keywords['dataset']
                #--------------------------------------------@
		#--- Extracting the members
		print 'Extracting info from '+filerootName+'.',
		sys.stdout.flush()
		classNames = ['TCanvas','RooDataSet','RooPlot','RooFitResult']
		fileroot = ROOT.TFile(filerootName)
		#--- Checking the extraction was fine
		if fileroot.IsZombie():
			message = '\033[1;31mpytnp: Invalid root dataset or root dataset not found, %s \033[1;m' % filerootName
			raise IOError, message
		#Building the dictionary 
		self.__dict__ = {}
		self.__dict__ = self.__extract__(fileroot, self.__dict__, dataset) 
		for name, dataSet in self.__dict__['RooDataSet'].iteritems():
			self[name] = dataSet
		print ''
		self.__fileroot__ = fileroot
		#-- Get the resonances names
		#--- If it does not provided by the user
		if not self.resonance:
			self.resonance, self.resLatex = getResName( filerootName )
		#--- Encapsulate the hierarchy of the directories: FIXME: Es realmente necesario??
		for name in self.iterkeys():
			self.__attrDict__ = self.__getType__(name,self.__attrDict__)

	def __getType__(self, name, structure):
		#FIXME: Es realmente necesario??
		"""
		__getType__( 'RooDataSet name', dictionary ) --> dictionary
		Build a dictionary where the key is the pathname (in standard T&P format)
		and the values are also dictionaries storing relevant info of the dataset.
		"""
		import re
		#-- Dictionary to store 
		structure[name] = { 'effType': {}, 'objectType': {}, 'methodUsed': {}, 'isMC' : {} }
		#-- Extracting
		pathname = name.split('/')
		if len(pathname) != 3:
			#-- The storege format is not in T6P standard
			message = '\033[1;31mThe format of the %s file is not in T&P standard... Exiting\033[1;m' % self.__fileroot__.GetName()
			print message
			exit(-1)
		effType = pathname[0]
		objectType = pathname[1]
		methodUsed = pathname[2]
		#-- Mapping
		#---- Type of efficiency
		if effType == 'histoTrigger':
			structure[name]['effType'] = 'trigger'
		elif effType == 'histoMuFromTk':
			structure[name]['effType'] =  'muonId'
		else:
			message = '\033[1;31mrd... I don\'t understand what efficiency is in the directory %s \033[1;m' % effType
		#setattr(self.RooDataSet, structure[name]['effType'], {})
		#---- Type of efficiency
		structure[name]['objectType'] = objectType.split('_')[0]
		#---- Method Used
		structure[name]['methodUsed'] = methodUsed
		#---- Is mcTrue
		regexp = re.compile( '\S*_(?P<mc>mcTrue)' ) #PRovisional o no...
		try:
			# Check if it mcTrue
			regexp.search( objectType ).group( 'mc' )
			structure[name]['isMC'] = 1
		except AttributeError:
			structure[name]['isMC'] = 0

		return structure


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
		try:
			listOfKeys = Dir.GetListOfKeys()
		##-- Checking that is a Tag and Probe fit 
		##   file. IF it is not, then we find
		##   some not expected TKeys (as TTree, etc.. )
		except AttributeError:
			message = """\033[1;31mpytnp: The root file is not an standard T&P fit file\033[1;m""" 
			raise AttributeError, message
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
	
	
	#TODO
	def write(self, fileOut):
		"""
		write( fileOut ) 

		Create a root file with all the RooDataSets of 
		the instance.
		"""
		f = ROOT.TFile(fileOut,'RECREATE')

		for name,dataSet in self.RooDataSet.iteritems():
			dataSet.Write(name.replace('/','_'))
		
		f.Close()

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


	def inferInfo( self, name ):
		"""
		inferInfo( name ) -> str

		Giving a standard directory-like name of an object,
		the function returns what kind of efficiency is,
		MuonID or Trigger.
		"""
		#TODO: Si mantegno __attrDict__ se puede extraer
		#      de ese diccionario dicrectamente
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
		bins, arrayBins = getBinning( v )
		rangeStr = hidVar+' range '
		rangeStr += '('+str(arrayBins[nBin])+','+str(arrayBins[nBin+1])+')'

		return rangeStr
		

	def plotEff1D( self, name ):
		#TODO: Cambiar esta funcion para que utilice el
		#      RooDataSet o ambos...
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
		ptNbins, arrayBinsPt = getBinning( pt )
		etaNbins, arrayBinsEta = getBinning( eta )
		#-- To avoid warning in pyROOT
		hTitleOfHist = 'h'+name.replace('/','_')
		h = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
		#h.SetTitle( title )
		#h = ROOT.TH2F( 'h', '', ptNbins, arrayBinsPt, etaNbins, arrayBinsEta )
	  	hlo = h.Clone("eff_lo")
	  	hhi = h.Clone("eff_hi")
		
		# To control the case where we don't have entries
		# If we don't have entries, b will be None
		b = None
		for i in xrange(dataSet.numEntries()):
			_dummy = dataSet.get(i)
			b = h.FindBin(eta.getVal(), pt.getVal())
#			print 'bin=',b,' pt =', pt.getVal(),' eta=',eta.getVal()
			h.SetBinContent(b, eff.getVal())
			h.SetBinError(b, (-eff.getErrorLo()+eff.getErrorHi())/2.0) # WATCH: Error 'Simetrized' 
			hlo.SetBinContent(b, eff.getVal()+eff.getErrorLo())
		if b:
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


