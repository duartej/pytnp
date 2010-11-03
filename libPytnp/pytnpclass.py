"""
"""
#TODO: Portar las funciones a utils. Crear una 
import ROOT  #BORRRRARLO
from ROOT import TFile
import sys

from getresname import *  #FIXME: OJO CON ESTO
from tnputils import *

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
	#-- Attribute dictionary
	__attrDict__ = {}
	#-- Binned variables introduced by user
	userVariables = None
	effName = 'eff'
	# Classes to store them
	classNames = ['TCanvas','RooDataSet','RooFitResult']
	def __init__(self, filerootName, **keywords):
		"""
                pytnp(filerootName, resonance=('name','nameLatex'), dataset='type', mcTrue=true, effName='efficiency_name',
		                                     variables=['varname1','varname2',..]  ) -> pytnp object instance

		Create a dictionary which are going to be populate
		with the plots and datasets already contained in the
		file.
		KEYWORDS:
			If 'dataset' is included, it will only  map 
			the object matching with 'dataset'.
			
			If 'resonance'=(name,latexName) is included the filename is not necessary
			to be an standard tag and probe NAME (i.e. Resonance_blabla.root).
			
			If 'mcTrue' is set to True it will store the mcTrue info
			and will associate each dataset with their mcTrue dataset.

			If effName is set, the user are providing the efficiency name which it will
			find inside the RooDataSets. Otherwise, we assume the name 'eff'.

			If 'variables' is included, only it will be considered the binned variables
			within the list

		The instance will contain the follow datamembers:
		    
		    TCanvas, RooDataSet, RooFitResults

		which again are dictionaries analogous of the 
		instance itself and can be extracted as datamembers.

		TODO: Put dictionary output
		"""
		#--- Checking the keys dictionary passed ----#
#				self.x = keywords[i][0]
#				self.y = keywords[i][1]
		dataset = self.__check_keywords__( keywords ) #FIXMEE

                #--------------------------------------------#
		#--- Extracting the members
		print 'Extracting info from '+filerootName+'.',
		sys.stdout.flush()
		fileroot = TFile(filerootName)
		#--- Checking the extraction was fine
		if fileroot.IsZombie():
			message = '\033[1;31mpytnp: Invalid root dataset or root dataset not found, %s \033[1;m' % filerootName
			raise IOError, message
		
		#Building the dictionary (__dict__ is a list containing the attributes and methods of a class)
		# In pytnp __dict__ contains the ...FIXME
		#--- Extract all the objects of the rootfile
		self.__dict__ = self.__extract__(fileroot, self.__dict__, dataset) 
		#--- Checking everything was fine
		if not 'RooDataSet' in self.__dict__.keys():
			message = """\033[1;31mpytnp: The root file is not an standard T&P fit file\033[1;m"""
			raise AttributeError, message
		print ''
		
		#--- Getting the variables names of the RooDataSet 
		#----- (By construction in CMSSW package all the RooDataSet
		#------ should contain the same variables) ------------------ FIXME: CUidado con esta aseveracion!!
		for dataset in self.__dict__['RooDataSet'].itervalues(): 
			self.variables = getVarInfo(dataset) 
			#break -> In principle all dataset must contain the same variables 

		#--- Check that efficiency is in there
		if not self.effName in self.variables.keys():
			try:
				message = """\033[1;33mError: The efficiency name introduce '%s' is not in the root file.
  I have these variables located:\033[1;m""" % keywords['effName']
			except KeyError:
				message = """\033[1;33mError: The efficiency name per default 'eff' is not in the root file. 
  You should introduced the name when instance the class =>   a = pytnp( 'filename.root', effName='whatever' )
  I have these variables located:\033[1;m"""
  			message += ' '
  			for i in self.variables:
				message += i+', '
			message = message[:-2]+'\n'
			print message
			raise KeyError
		
		#--- Check the variables introduced by user are there and
		#------ Setting the binned Variables: extract efficiencies from last list
		message = ''
		_errorPrint = False
		self.binnedVar = []
		try:
			for var in self.userVariables:
				if not var in self.variables:
					message += """\033[1;33mError: Variable '%s' is not in the root file.\n\033[1;m""" % var
					_errorPrint = True
				else:
					self.binnedVar[var] = self.variables[var] 
		except TypeError:
			#The user didn't introduce binned variables, I take everyone
			self.binnedVar = dict([ (var, self.variables[var]) for var in filter( lambda x: x.lower().find(self.effName) == -1, self.variables ) ])
			#self.binnedVar = filter( lambda x: x.lower().find(self.effName) == -1, self.variables ) 
		if _errorPrint:
			message += """\033[1;33m  I found this variables in your file: """
			for var in self.variables:
				message += var+', '
			message = message[:-2]+'\033[1;m'
			raise UserWarning, message
		self.eff = filter( lambda x: x.lower().find(self.effName) != -1, self.variables )[0]


		self.__fileroot__ = fileroot
		#-- Get the resonances names
		#----- If it does not provided by the user
		if not self.resonance:
			self.resonance, self.resLatex = getResName( filerootName )
		#--- Encapsulate the hierarchy of the directories:
		for name in self.__dict__['RooDataSet'].iterkeys():
			self.__attrDict__ = self.__getType__(name,self.__attrDict__)
		#--- Associate the names of the mcTrue and counting MC True to a fit_eff
		#----- Getting all the MC True RooDataSets: [ (name,dictionary),...]
		mcTrueData = filter( lambda x: x[1]['isMC'] == 1, self.__attrDict__.iteritems() )
		#---- Loop over all RooDataSets fitted but not MC
		for Name,Dict in filter( lambda x: x[1]['isMC'] == 0 and x[1]['methodUsed'] == 'fit_eff', self.__attrDict__.iteritems() ):
			#---- Getting the parter to mcTrueData: all with the same objectType and effType 
			#------ Can be cnt, fit_eff and sbs
			partner = filter( lambda x: x[1]['objectType'] == Dict['objectType'] and x[1]['effType'] == Dict['effType'], \
					mcTrueData )
			#--- Looping over the MC RooDataSet which is the same efficiency type and category as the fitted RooDataSets
			for mcName, mcDict in partner:
				#---- Only want the reference to fit_eff and cnt_eff mcTrue
				if mcDict['methodUsed'] == 'fit_eff' or mcDict['methodUsed'] == 'cnt_eff' :
					try:
						self.__attrDict__[Name]['refMC'][ mcDict['methodUsed'] ] =  mcName 
					except KeyError:
						self.__attrDict__[Name]['refMC'] = { mcDict['methodUsed'] : mcName }
		_prov = set()
		#--- The dictionary itself contains only the RooDataSets
		for name, dataSet in self.__dict__['RooDataSet'].iteritems():
			#try:
			self[name] = self.__attrDict__[name]
				# To get also the no fit_eff --> Except sbs (not implemented yet) and cnt no MC
			#except KeyError:
			#	self[name] = self.__getType__(name,{})[name]
				#--- Skipping sbs, cnt no MC
			if self.__attrDict__[name]['methodUsed'] == 'sbs_eff': #or \
					#	( self.__attrDict__[name]['methodUsed'] == 'cnt_eff' and self.__attrDict__[name]['isMC'] == 0):
				self.pop(name)
				continue

			self[name]['dataset'] = dataSet
			#self[name]['variables'] = getVarInfo(dataSet)
			#self[name]['ArgSet']
			#--To store the categories we have
			_prov.add( self[name]['objectType'] )
		#--- We are not interested about the MC, only in cnt and fit_eff
		map( lambda (Name,Dumm): self.__attrDict__.pop(Name), mcTrueData )
		#--- We are not interested about the sbs and cnt not MC
		map( lambda y: self.__attrDict__.pop( y[0] ), filter( lambda x: x[1]['isMC'] == 0 and x[1]['methodUsed'] != 'fit_eff',\
				self.__attrDict__.iteritems() ) ) 
		#-- Storing the categories we have 
		self.categories = list(_prov)


	def __check_keywords__(self, keywords ):
		"""
		Internal use: to check the keywords passed to the constructor
		"""
		#FIXME : ojo, dataset ha quedado huerfana...
		#--- Keys valid
		valid_keys = ['resonance', 'dataset', 'mcTrue','variables', 'effName' ]
		#---- Some initializations using user inputs ---#
		dataset = ''
		for i in keywords.keys():
			if not i in valid_keys:
				message = '\033[1;31mpytnp: invalid instance of pytnp: you can not use %s as key argument, ' % i
				message += ' key arguments valids are \'resonance\', \'dataset\', \'mcTrue\', \'variables\', \'effName\' \033[1;m' 
			#	print help(self.__init__)
				raise IOError, message
			#---Checking the correct format and storing
			#---the names provided by the user
			elif i == 'resonance':
				#Message to be sended if the value is not a tuple
				message ='\033[1;31mpytnp: Not valid resonance=%s key; resonance key must be a tuple containing (\'name\',\'nameInLatex\')\033[1;m' \
						% str(keywords['resonance'])
				if len(keywords['resonance']) != 2:
					print message
					raise KeyError
				else:
					#Checking the tuple format is (name, nameInLatex)
					if keywords['resonance'][0].find('#') != -1 \
							or keywords['resonance'][0].find('{') != -1  :
						print message		
						raise KeyError
					#--- Storing resonance provided by user
					self.resonance = keywords['resonance'][0]
					self.resLatex  = keywords['resonance'][1]
			elif i == 'effName':
				self.effName = keywords[i]
			elif i == 'dataset':
				dataset = keywords[i]
			elif i == 'variables':
				#-- Sanity checks
				if not isinstance(keywords[i], list):
                                        message ='\033[1;31mpytnp: Not valid \'variables=%s\' key; must be a tuple containing n variables names\033[1;m' % str(keywords[i])
					print message
					raise KeyError
				else:
					self.userVariables = [ var for var in keywords[i] ]
		return dataset

	def __str__(self):
		"""
		used by print built-in function
		"""
		message = ''
		for name, Dict in self.iteritems():
			message += '-- \033[1;29m'+name+'\033[1;m\n'
			for key,value in sorted(Dict.iteritems()):
				message += '     %s: %s ' % (key,str(value))
				message += '\n'	

		return message

	def __getType__(self, name, structure):
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
			message = '\033[1;33mWarning: I don\'t understand what efficiency is in the directory %s \033[1;m' % effType
			#print message
			#Patch to new version of Tag and probe  (3.8.X)
			structure[name]['effType'] = 'unknown'
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
		        elif className in self.classNames:
	 		#elif className == 'TCanvas' or className == 'RooFitResult' or className == 'RooDataSet' or \
	 		#		className == 'RooPlot':
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
	
	## Getters for attributes ######################################################################
	def getCategory( self, name ):
		"""
		getCategory( name ) -> 'category'

		Getting the name of the object, return the category belongs to 
		"""
		try:
			return self.__attrDict__[name]['objectType']
		except KeyError:
			message = """\033[1;33mWarning: The %s is not a fit_eff RooDataSet\033[1;m""" % name
			print message
			return None
	
	def getFitEffList( self ):
		"""
		getFitEffList() -> [ 'name1', ... ]

		Returns a string's list of the names of RooDataSet which are fit_eff
		"""
		fitEffList = []
		for name,Dict in filter( lambda (name,Dict): Dict['methodUsed'] == 'fit_eff' ,self.__attrDict__.iteritems() ):
			fitEffList.append( name )
		
		if len(fitEffList) == 0:
			message = """\033[1;33mWarning: There is no fit_eff RooDataSet in this file\033[1;m"""
			print message
			return None

		return fitEffList
	
	def getCountMCName( self, name ):
		"""
		getCountMCName( name ) -> 'nameMCcountig'

		Gived the RooDataSet name (fit_eff like), returns the name of its MC True counting equivalent.
		"""
		try:
			return self.__attrDict__[name]['refMC']['cnt_eff']
		except KeyError:
			message = """\033[1;33mWarning: The is no counting MC True information associated with %s RooDataSet\033[1;m""" % name
			print message
			return None
	## Getters for attributes ######################################################################

	def write(self, fileOut):
		"""
		write( fileOut ) 

		Create a root file with all the RooDataSets of 
		the instance.
		"""
		f = ROOT.TFile(fileOut,'RECREATE')
		if f.IsZombie():
			message = '\033[1;31mCannot open %s file. Check your permissions\033[1;m' % fileOut
			raise IOError, message

		for name,dataSet in self.RooDataSet.iteritems():
			dataSet.Write(name.replace('/','_'))
		try:
			for name,histoTuple in self.TH2F.iteritems():
				for histo in histoTuple:
					#Watch out: not use the key name because we have 3 histos
					histo.Write('TH2F_'+histo.GetName().replace('/','_'))
		except AttributeError:
			print "\033[1;33mWarning: Do not stored any TH2F map. You must use 'plotEff2D' method first.\033[1;m"

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

		
	def plotEff1D( self, name, inputVarName, Lumi ):
		"""
		plotEff1D( RooDataSet, 'variable_name', 'latex string Luminosity' ) 
	
		Given a name directory-like for a ROOT.RooDataSet object,
	 	the function creates a 1-dim plot of 'variable_name' extracted from the
		object and it will save it in a eps file. Also
		it will store the graph object:
		                      self[nameRooDataSet]['tgraphs'] = { 'graph_name': TGraphAsymmErrors, ... }
		"""
		dataset = None
		#-- Checking if the object exists
		try:
			dataset = self.RooDataSet[name]
		except KeyError:
		  	print """\033[1;31mpytnp.plotEff1D Error: you must introduce a valid name, %s is not a RooDataSet in the root file\033[1;m""" % name
			raise KeyError
		#--- Empty dataset
		if self.RooDataSet[name].numEntries() == 0:
			message = """\033[1;34mpytnp.plotEff1D: Empty RooDataSet %s. Skipping...\033[1;m""" % name
			print message
			return None
		#--- Checking variable
		if not inputVarName in self.binnedVar.keys():
		  	print """\033[1;31mpytnp.plotEff1D Error: you must introduce a valid binned variable name, '%s' is not in the '%s' RooDataSet\033[1;m""" % (inputVarName,name )
			print """\033[1;31mpytnp.plotEff1D:  The list of binned variables are %s\033[1;m""" % str(self.binnedVar.keys())  
			raise KeyError
		
		self[name]['tgraphs'] = {}		
		# Special case: we have only one variable
		if len(self.binnedVar) == 1:
			graphName = self[name]['methodUsed']+'_'+self[name]['effType']+'_'+\
					self[name]['objectType']+'__'
                        if self[name]['isMC'] == 1:
				graphName += '__mcTrue'
			#--- Extracting the efficiency values per bin
			plotList = tableEff( dataset )
			graph = ROOT.TGraphAsymmErrors()
			graph.SetName( graphName )
			graph.SetMarkerSize(1)	
			_min = 0
			_max = 0
			entry = 0
			#--- Setting the points and extracting the min and max value
			#--- in order to build the frame to plot
			for varDict in plotList:  
				(eff,effLo,effHi) = varDict[self.effName]
				(var,varLo,varHi) = varDict[inputVarName]
				graph.SetPoint(entry, var, eff )
				graph.SetPointEXlow( entry, var-varLo )
				graph.SetPointEXhigh( entry, varHi-var )
				graph.SetPointEYlow( entry, eff-effLo )
				graph.SetPointEYhigh( entry, effHi-eff )

				_min = min( _min, varLo )
				_max = max( _max, varHi )
				entry += 1
			#--- Cosmethics and storing the plot
			title = self[name]['objectType']+' category'
			c = ROOT.TCanvas()
			frame = c.DrawFrame(_min,0,_max,1.05)
			frame.SetName( 'frame_'+graphName )
			frame.SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
			graph.SetTitle( '' )
			frame.GetXaxis().SetTitle(self.variables[inputVarName]['latexName']+' '+self.variables[inputVarName]['unit'])
			graph.GetXaxis().SetTitle(self.variables[inputVarName]['latexName']+' '+self.variables[inputVarName]['unit'])
			frame.GetYaxis().SetTitle( '#varepsilon' )
			graph.GetYaxis().SetTitle( '#varepsilon' )
			frame.Draw()
			graph.Draw('P')
			c.SaveAs( graph.GetName()+'.eps' )
			c.Close()

			self[name]['tgraphs'][ graph.GetName() ] = graph 

			return 

		
		#-- More than one binned variable
		for varName in filter( lambda x: x != inputVarName, self.binnedVar.keys()):
                        _otherVarList_ = filter( lambda x: x != varName, self.binnedVar.keys() )
                        _otherVar_ = ''
                        for i in _otherVarList_:
                                _otherVar_ += i+', '
                        _otherVar_ = _otherVar_[:-2]
                        if len(_otherVar_ ) != 0:
                                _otherVar_ = ' in all the range of ' +_otherVar_
                        print '\033[1;34m   \''+varName+'\' bins'+_otherVar_+'\033[1;m'

                        #--- Extracting bins and array of bins
                        binsN = self.variables[varName]['binN']
                        arrayBins = self.variables[varName]['arrayBins']
                        for bin in xrange(binsN):
                                arrayBins = self.variables[varName]['arrayBins']
                                Lo = arrayBins[bin]
                                Hi = arrayBins[bin+1]
                                Central = (Hi+Lo)/2.0
                                graphName = self[name]['methodUsed']+'_'+self[name]['effType']+'_'+\
                                                self[name]['objectType']+'__'+varName+'_bin'+str(bin)+'_'
                                #Getting list of efficiency values plus variables
                                _plotList = eval('getEff(dataset,self.effName,'+varName+'='+str(Central)+')')
                                #print _plotList
                                #Extracting info to plot
				#try:
                                (eff,effErrorLo,effErrorHi),otherVarDict = _plotList[0]

                                if len(filter( lambda (eff,__dic): eff[0] == 0.0, _plotList )) == len(_plotList):
					print '\033[1;33mpytnp.plotEff1D: Warning: skipping, efficiencies in the dataset not calculated\033[1;m'
                                        continue
                                graph = {}
                                _max = {}
                                _min = {}
                                for otherVarName, val in otherVarDict.iteritems():
                                        graphName = graphName+otherVarName
                                        if self[name]['isMC'] == 1:
                                                graphName += '__mcTrue'
                                        graph[otherVarName] = ROOT.TGraphAsymmErrors()
                                        graph[otherVarName].SetName( graphName )
                                        graph[otherVarName].SetMarkerSize(1)
                                        _max[otherVarName] = 0.0
                                        _min[otherVarName] = 0.0
                                entry = 0
                                for (eff,effLo,effHi),otherVarDict in _plotList:
                                        for otherVarName, (central, low, high) in otherVarDict.iteritems():
                                                _min[otherVarName] = min( _min[otherVarName], low )
                                                _max[otherVarName] = max( _max[otherVarName], high )
                                                graph[otherVarName].SetPoint(entry, central, eff )
                                                graph[otherVarName].SetPointEXlow( entry, central-low )
                                                graph[otherVarName].SetPointEXhigh( entry, high-central)
                                                graph[otherVarName].SetPointEYlow( entry, eff-effLo )
                                                graph[otherVarName].SetPointEYhigh( entry, effHi-eff )
                                        entry += 1

                                #-- Nota que ya tienes definido otherVar unas lineas mas arriba
                                title = self.resLatex+', ('+str(Lo)+','+str(Hi)+') '+self.variables[varName]['latexName']+' range, '
                                title += self[name]['objectType']+' category'
                                for otherVarName, (central, low, high) in otherVarDict.iteritems():
                                        c = ROOT.TCanvas()
                                        frame = c.DrawFrame(_min[otherVarName],0,_max[otherVarName],1.05)
                                        frame.SetName( 'frame_'+graphName )
                                        #frame.SetTitle( title ) ---> Out titless
                                        frame.SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
                                        #frame.SetTitle( '' )
                                        #graph[otherVarName].SetTitle( title ) --> Out titles
                                        graph[otherVarName].SetTitle( '' )
                                        frame.GetXaxis().SetTitle(self.variables[otherVarName]['latexName']+' '+self.variables[otherVarName]['unit'])
                                        graph[otherVarName].GetXaxis().SetTitle(self.variables[otherVarName]['latexName']+' '+self.variables[otherVarName]['unit'])
                                        frame.GetYaxis().SetTitle( '#varepsilon' )
                                        graph[otherVarName].GetYaxis().SetTitle( '#varepsilon' )
                                        frame.Draw()
                                        graph[otherVarName].Draw('P')
                                        c.SaveAs( graph[otherVarName].GetName()+'.eps' )
                                        c.Close()
                                        self[name]['tgraphs'][graph[otherVarName].GetName()] = graph[otherVarName]


	
	def plotEff2D( self, name, Lumi, **keywords ):
		"""
		plotEff2D( name, x='var1', y='var1' ) 

		Giving a RooDataSet name in directory-like format,
		the function will do a bi-dimensional plot of 
		efficiency with pt and eta variables. Also, it
		will stores in the object instance
		"""
		#FIXME: Meter los errores en la misma linea (ahora te salta
		#       de linea (TEXT option)
		try:
			dataSet = self.RooDataSet[name]
		except KeyError:
			message = """\033[1;33mpytnp.plotEff2D Error: there is no RooDataSet with name %s\033[1;m""" % name
			print message
			print plotEff2D.__doc__
			raise KeyError
		x = None
		y = None
		hasVars = 0
		for axis, varName in keywords:
			if axis != 'x' or axis != 'y':
				message = """\033[1;33mpytnp.plotEff2D Error: the keyword %s is not valid. Use 'x' and 'y' as keywords\033[1;m""" % axis
				print message
				raise KeyError
			else:
				hasVars +=1
		if hasVars == 2:
			x = keywords['x']
			y = keywords['y']
		else:
			#Default
			x = self.binnedVar[0] #FIXME: Control Errores
			y = self.binnedVar[1] #FIXME: Control Errores 

		#--- Name for the histo and for the plot file to be saved
		histoName = 'TH2F_'+name
		#--- Checking if the histo is already stored and plotted
		if self.has_key(histoName):
			#-- Skipping, work it's done!
			return None
		#---- Preparing all the stuff
		title = self.resLatex+', '+self[name]['objectType']+' '+self[name]['effType']+' '+dataSet.GetTitle()
		yNbins = self.variables[y]['binN']
		#arrayBinsY = self.variables[y]['arrayBins']---> # I need the PyDoubleBuffer
		#------------------------------------------
		__argSet__ = dataSet.get()
		dum, arrayBinsY = getBinning( __argSet__[y] )
		#------------------------------------------
		xNbins = self.variables[x]['binN']
		#arrayBinsX = self.variables[x]['arrayBins']---> # I need the PyDoubleBuffer
		#------------------------------------------
		dum, arrayBinsX = getBinning( __argSet__[x] )
		#------------------------------------------
		hTitleOfHist = name.replace('/','_')
		h = ROOT.TH2F( hTitleOfHist, '', xNbins, arrayBinsX, yNbins, arrayBinsY ) 
	  	hlo = h.Clone("eff_lo")
		hlo.SetName( 'low_'+hTitleOfHist )
		hhi = h.Clone("eff_hi")
		hhi.SetName( 'high_'+hTitleOfHist )
		#-- Getting the efficiencies
		_tableEffList = tableEff(self.RooDataSet[name])
		skipPoints = False
		for binDict in _tableEffList:
			#-- Extract error values
			if abs(binDict[self.eff][0]-self.badPoint[0]) < 1e-9:
				skipPoints = True
				continue
			b = h.FindBin( binDict[x][0] , binDict[y][0] )
			h.SetBinContent(b, binDict[self.eff][0])
			h.SetBinError(b, (binDict[self.eff][2]-binDict[self.eff][1])/2.0 ) # WATCH: Error 'Simetrized' 
			hlo.SetBinContent(b, binDict[self.eff][1])
			hhi.SetBinContent(b, binDict[self.eff][2])
		c = ROOT.TCanvas()
		#c.SetLogy(isLog[1]) 
		h.GetYaxis().SetTitle(self.variables[y]['latexName'])
		h.GetXaxis().SetTitle(self.variables[x]['latexName'])
		h.GetZaxis().SetTitle(self.variables[self.eff]['latexName'])
		#h.SetTitle( title ) --> Out titles
		h.SetTitle( '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  ' )
		#h.SetTitle('' ) 
		h.Draw('COLZ')
		htext = h.Clone('htext')
		htext.SetMarkerSize(1.0)
		htext.SetMarkerColor(1)
		#if isLog[1]:
		#	ROOT.gStyle.SetPaintTextFormat("1.2f")
		#	htext.Draw('ESAMETEXT0')
		#else:
		ROOT.gStyle.SetPaintTextFormat("1.3f")
		#htext.SetMarkerSize(2.2)
		htext.Draw('SAMETEXTE0')
		#plotName = self.resonance+'_'+name.replace('/','_')+isLog[0]+'.eps'
		plotName = self.resonance+'_'+name.replace('/','_')+'.eps'
		c.SaveAs(plotName)

		if skipPoints:
			message = '\033[1;33mplotEff2D Warning: Some efficiencies points are failed in the fit, the last plot will skip values with %.4f\033[1;m' % self.badPoint[0]
			print message

		#FIXME: Ponerlo en el diccionario del RooDataSEt
		try:
			self.TH2F[histoName] = (h, hlo, hhi)
		except AttributeError:
			self.__setattr__('TH2F',{}) 
			self.TH2F[histoName] = (h, hlo, hhi)


