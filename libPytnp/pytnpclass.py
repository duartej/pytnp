"""
Module for the encapsulation of the Tag and Probe CMSSW N-tuple
"""
import sys

from management import printError, printWarning

class pytnp(dict):
	"""
	Class to retrieve and encapsulate the *tag and probe*
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
	userVariables = []
	effName = 'efficiency'
	#-- User enters the effType, objectType and isMC attributes
	configfile = None
	# Classes to store them
	classNames = ['RooDataSet']#,'RooFitResult','TCanvas']
	# CONSTRUCTOR ------------------------------------------------------------------------------------------------------
	def __init__(self, filerootName, **keywords):
		""".. class:: pytnp(filerootName [, resonance=(id,nameLatex), effName='efficiency_name', variables=[varname1,varname2,..], configfile=file,  dataset=type, mcTrue=true ] )
		
		Class encapsulating the contents of a Tag and Probe root file (generated from CMSSW T&P package).
		The root file must have a two-level directory hierarchy, where the RooDataSet 
		(whose actually contains the information) is in the bottom. The pytnp class is based
		in the RooDataSet, a instance of this class returns a dictionary (self) whose keys are
		the names (absolute path) of the RooDataSet, the values are dictionaries themselves with 
		keys storing useful information of the RooDataSet. A generic example is shown::

		  { 
		    'firstlevel/secondlevel/dataset_eff': { 
						           'effType': efficiency_type
						           'binnedVar': binnedvardict
						           'methodUsed': method_used
						           'variables': vardict
						           'dataset': roodataset
						           'isMC': 0|1
						           'eff': efficiencyname
						           'objectType': object_type
						          },
		     ....,
                  }

		where ``firstlevel/secondlevel/dataset_eff`` is the name of the dataset, the
		dictionary values have a ``efficiency_type``, ``method_used`` and ``object_type``
		strings which they going to be extracted from the root file or from the configuration
		file provided by the user. The keys ``binnedVar`` and ``variables`` are 
		dictionaries which contains useful information for the binned variables and all 
		the variables (respectively) in the RooDataSet (see :mod:`pytnp.libpytnp.tnputils.getVarDict`).
		The ``dataset`` key contains the RooDataSet object itself.

		The ``configfile`` keyword can be used to change the values found by the constructor
		when parsing the root file. An example of configuration file::

		    DataNames = { 
		                   # root file name: TnP_Z_DATA_TriggerFromMu_Trigger_ProbeMu11_Eta_Fit.root
				   'ProbeMu11_Eta_Fit': ( "Z#rightarrow#mu#mu, HLTMu11 trigger",'Z_11' ),
				   # root file is: TnP_Z_DATA_TriggerFromMu_Trigger_ProbeMu9_Eta_Fit.root
				   'ProbeMu9_Eta_Fit' : ("Z#rightarrow#mu#mu, HLTMu9 trigger", 'Z_9' ),
				}
		    #Attributes
		    Z_11 = {
		            'tpTree/PASSING_all/fit_eff': ( 'HLT_trigger' , 'Glb_muons' , 0 ),
			    'tpTree/PASSING_all/cnt_eff': ( 'HLT_trigger' , 'Glb_muons' , 1 ),
                           }
	            
		    Z_9  = {
		            'tpTree/PASSING_all/fit_eff': ( 'HLT_trigger' , 'Glb_muons' , 0 ),
			    'tpTree/PASSING_all/cnt_eff': ( 'HLT_trigger' , 'Glb_muons' , 1 ),
			   }

		The ``DataNames`` is a mandatory dictionary. It is used to identify a root file with 
		a ``pytnpname``, the keys are expressions which can describe the name of the 
		root file (using the ``find`` method of a string) and the values are tuples of strings
		with the latex name (to be put in the legends) and the ``pytnpname``. Using this
		identifier it possible to construct another dictionaries with the informationn of
		each dataset (or some dataset) in the root file. The names of the dictionary objects
		must be the same as the ``pytnpname`` defined before; this dictionaries have as keys
		the name of the datasets to be modified and the values are tuples with the 
		``effType``, ``objectType`` and ``isMC`` attributes.


		:param filerootName: name of the root file
		:type filerootName: string		
		:keyword resonance: assigns a (pytnpname,latexName) 
		:type resonance: (strings,string)
		:keyword effName: Providing the efficiency name finded inside the RooDataSets. 
		                  Otherwise, we assume the name ``efficiency``.
				  CAVEAT: all the RooDataSet MUST have the same efficiency name.
		:type effName: string
		:keyword variables: Binned variables considered
		:type variables: list of strings
		:keyword configfile: the configuration file to be used (if any)
		:type configfile: string
		:keyword dataset: Store only dataset matching this effType (TO BE DEPRECATED)
		:type dataset: string
		:keyword mcTrue: Setting True, it stores the mcTrue info and will associate each
		                 dataset with their mcTrue dataset. (TO BE DEPRECATED)
		:type mcTrue: bool

		
		:raise IOError: Invalid root file name
		:raise TypeError: Invalid format of the root file (do not have the proper directory structure)
		:raise KeyError: Invalid name of efficiency, not found in the dataset
		:raise ValueError: Not found the binned variables introduced

		"""
		import ROOT
		from getresname import getResName
		from tnputils import getVarDict, isEffNoNull

		#--- Checking the keys dictionary passed ----#
		dataset = self.__check_keywords__( keywords ) #FIXMEE

		#--- Extracting the members
		print 'Extracting info from '+filerootName+'.',
		sys.stdout.flush()
		fileroot = ROOT.TFile(filerootName)
		#--- Checking the extraction was fine
		if fileroot.IsZombie():
			message = 'Invalid root dataset or root dataset not found, \'%s\'' % filerootName
			printError( self.__module__, message, IOError )
		
		#--- Extract all the objects of the rootfile and put them as attributes of the instance
		self.__dict__ = self.__extract__(fileroot, self.__dict__, dataset) 
		#--- Checking everything was fine
		if not 'RooDataSet' in self.__dict__.keys():
			message = """The root file is not an standard T&P fit file"""
			printError( self.__module, message, TypeError )
		print ''

		self.__fileroot__ = fileroot
		#-- Get the resonances names
		#----- If they had not been provided by the user
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
		#todelete = []
		for name, dataSet in self.__dict__['RooDataSet'].iteritems():
			#try:
			self[name] = self.__attrDict__[name]
				# To get also the no fit_eff --> Except sbs (not implemented yet) and cnt no MC
			#except KeyError:
			#	self[name] = self.__getType__(name,{})[name]
				#--- Skipping sbs, cnt no MC
			#**if self.__attrDict__[name]['methodUsed'] == 'sbs_eff': #or \
					#	( self.__attrDict__[name]['methodUsed'] == 'cnt_eff' and self.__attrDict__[name]['isMC'] == 0):
			#**	self.pop(name)
			#**	todelete.append( name )
			#**	continue

			self[name]['dataset'] = dataSet
			#--To store the categories we have
			_prov.add( self[name]['objectType'] )
		#--- We are not interested about the MC, only in cnt and fit_eff
		#**map( lambda (Name,Dumm): self.__attrDict__.pop(Name), mcTrueData )
		#--- We are not interested about the sbs and cnt not MC
		#**map( lambda y: self.__attrDict__.pop( y[0] ), filter( lambda x: x[1]['isMC'] == 0 and x[1]['methodUsed'] != 'fit_eff',\
		#		self.__attrDict__.iteritems() ) ) 
		#-- Storing the categories we have 
		self.categories = list(_prov)
		#--- Don-'t forget delete also in RooDataSet attribute
		#for name in todelete:
		#	self.RooDataSet.pop( name )
		
		#----- Variables, binned, efficiency, user introduced, ...
		#--- The list will contain those dataset which don't have anyone of the variables entered  
		#--- by the user (in case the user enter someone) and the datasets will be removed
		deleteDataset = set([])
		#--- Getting the variables names of the RooDataSet 
		for name, dataset in self.RooDataSet.iteritems(): 
			self[name]['variables'] = getVarDict(dataset)
			#--- Check that efficiency is in there
			if not self.effName in self[name]['variables'].keys():
				try:
					message = """The efficiency name introduce '%s' is not in the '%s' RooDataSet.\n""" % (keywords['effName'], name )
					message += """I have these variables located:""" 
                                except KeyError:
				        message = """The efficiency name per default 'efficiency' is not in the '%s' RooDataSet.\n""" 
					message +="""You should introduced the name when instance the class =>"""\
							""" a = pytnp( 'filename.root', effName='whatever' )\n"""\
							"""I have these variables located:"""
                                message += ' '
				for i in self[name]['variables']:
					message += i+', '
				message = message[:-2]
				message += '\n\033[1;33m  CAVEAT: The efficiency name \033[1;m\033[1;39mMUST\033[1;m\033[1;33m'\
						'have the same name for all the RooDataSets in the rootfile\033[1;m'	
				printError( self.__module__+'.pytnp', message, KeyError )
			#--- Check the variables introduced by the user are there and
			#------ Setting the binned Variables: extract efficiencies from last list
			message = ''
			_warningPrint = False
			_havetodelete = False
			lostVar = ''
			self[name]['binnedVar'] = {}
			if len(self.userVariables) != 0 :
				for var in self.userVariables:
					if not var in self[name]['variables']:
						lostVar += var+', '
						_warningPrint = True
						_havetodelete = True
					else:
						self[name]['binnedVar'][var] = self[name]['variables'][var] 
				if _havetodelete:
					deleteDataset.add( name ) 
				if _warningPrint:
					lostVar = lostVar[:-2]
					message += """Variable '%s' is not in the '%s' RooDataSet. Skipping it... """ % ( lostVar,name)
					printWarning( self.__module__+'.pytnp', message )
			else:
				#The user didn't introduce binned variables, I take everyone
				self[name]['binnedVar'] = dict([ (var, self[name]['variables'][var]) \
						for var in filter( lambda x: x.lower().find(self.effName) == -1, self[name]['variables'] ) ])
				#if _errorPrint:
				#	message += """  ----> I found: """
				#	for var in self[name]['variables']:
				#		message += var+', '
				#		message = message[:-2]
				#		printError( self.__module__, message, UserWarning )
			self[name]['eff'] = filter( lambda x: x.lower().find(self.effName) != -1, self[name]['variables'] )[0]

		for _dataout in deleteDataset:
			self.pop( _dataout )
			self.RooDataSet.pop( _dataout )
			self.__attrDict__.pop( _dataout )
		
		#-- Something wrong if we pop out all the datasets we had
		if len(self) == 0:
			message = """There is no RooDataSet that fulfill the binned variables introduced""" 
			printError( self.__module__, message, ValueError )


		#--- Extracting those RooDataSet which have null values of efficiency
		_todelete = []
		for name, _datasetObject in self.RooDataSet.iteritems():
			if not isEffNoNull( _datasetObject, self.effName ):
				_todelete.append( name )
				del _datasetObject
				message = "The RooDataSet '%s' have all '%s' values null. Skipping the storage..." % (name, self.effName)
				printWarning( self.__module__+'.pytnp', message )
		map( lambda name: self.pop( name ), _todelete )
		map( lambda name: self.__attrDict__.pop( name ), _todelete )
		for __attr in self.classNames:
			map( lambda name: self.__getattribute__( __attr ).pop( name ) , _todelete )
	# END CONSTRUCTOR ---------------------------------------------------------------------------------------------------


	def __check_keywords__(self, keywords ):
		""".. method:: __check_keywords__( keywords ) 

		Checks the keywords passed to the constructor

		:raise KeyError: invalid keyword
		:raise TypeError: invalid format of ``variables``
		"""
		#FIXME : ojo, dataset ha quedado huerfana...
		#--- Keys valid
		valid_keys = ['resonance', 'dataset', 'mcTrue','variables', 'effName', 'configfile' ]
		#---- Some initializations using user inputs ---#
		dataset = ''
		for i in keywords.keys():
			if not i in valid_keys:
				message = 'Invalid instance of pytnp: you can not use %s as key argument, ' % i
				message += 'key arguments valids are \'%s\'' % str(valid_keys)
			#	print help(self.__init__)
				printError( self.__check_keywords__.__module__+'.___check_keywords__', message, KeyError )
			#---Checking the correct format and storing
			#---the names provided by the user
			elif i == 'resonance':
				#Message to be sended if the value is not a tuple
				message ='Not valid resonance=%s key; resonance key must be a tuple containing (\'name\',\'nameInLatex\')' \
						% str(keywords['resonance'])
				if len(keywords['resonance']) != 2:
					printError( self.__module__, message, KeyError )
				else:
					#Checking the tuple format is (name, nameInLatex)
					if keywords['resonance'][0].find('#') != -1 \
							or keywords['resonance'][0].find('{') != -1  :
						printError( self.__module__, message, KeyError )
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
                                        message ='Not valid \'variables=%s\' key; must be a list containing n variables names' % str(keywords[i])
					printError( self.__module__, message, TypeError )
				else:
					self.userVariables = [ var for var in keywords[i] ]
			elif i == 'configfile':
				self.configfile = keywords[i]
			#elif i == 'mcTrue' --> TO BE DEPRECATED OR ACTIVATED?

		return dataset

	def __str__(self):
		"""
		used by print built-in function
		"""
		message = '\033[1;39m'+self.resonance+'::\033[1;m\n'
		for name, Dict in self.iteritems():
			message += '-- \033[1;29m'+name+'\033[1;m\n'
			for key,value in sorted(Dict.iteritems()):
				if isinstance(value,dict):
					message += '     %s: %s (keys of the dictionary)' % (key,str(value.keys()))
					message += '\n'	
				else:
					message += '     %s: %s ' % (key,str(value))
					message += '\n'	

		return message

	
	def __repr__(self):
		"""
		representation of the object
		"""
		return "<pytnp class instance>"

	def __getType__(self, name, structure):
		""".. method:: __getType__( 'RooDataSet name', dictionary ) -> dictionary

		Build a dictionary where the key is the pathname (in standard T&P format)
		and the values are also dictionaries storing relevant info of the dataset.

		:raise ValueError: file root format incorrect
		:raise AttributeError: Misuse of configuration file
		"""
		import re
		from management import parserConfig
		#-- Dictionary to store 
		structure[name] = { 'effType': {}, 'objectType': {}, 'methodUsed': {}, 'isMC' : {} }
		#-- Extracting
		pathname = name.split('/')
		if len(pathname) != 3:
			#-- The storage format is not in T6P standard
			message = 'The format of the \'%s\' file is not in T&P standard.' % self.__fileroot__.GetName()
			printError( self.__module__, message, ValueError )

		effType = pathname[0]
		objectType = pathname[1]
		methodUsed = pathname[2]
		#-- Mapping
		#--- Check and put values provided by the user
		try:
			#--- If not enter config, self.configfile is None and 
			#--- parserConfig raise a TypeError exception.
			#--- If is not there some key, the AttributeError is raised
			try:
				tupleAttr = parserConfig( self.configfile, self.resonance+'::'+name )
			except AttributeError:
				Message = "If the error above is related with the identifier:\n"
				Message += "Coherence broken between configuration file and 'pytnp' instanciation\n"
				Message += "Check you have a object called '%s' in your configuration file" % self.resonance
				printError( self.__module__+'.pytnp', Message, AttributeError )
			#--- If nothing the tupleAttr is None so NameError exception too
			structure[name]['effType'] = tupleAttr[0]
			structure[name]['objectType'] = tupleAttr[1]
			structure[name]['isMC'] = tupleAttr[2]
			#FIXME: To be implemented
			#try:
			#	structure[name]['legend'] = tupleAttr[3]
			#except IndexError:
			#	pass
		except (NameError,TypeError):
			#---- Type of efficiency
			if effType == 'histoTrigger':
				structure[name]['effType'] = 'Trigger'
			elif effType == 'histoMuFromTk':
				structure[name]['effType'] =  'MuonID'
			else:
				structure[name]['effType'] = 'unknown'
			#---- Type of efficiency
			structure[name]['objectType'] = objectType.split('_')[0]
			#---- Is mcTrue
			regexp = re.compile( '\S*_(?P<mc>mcTrue)' )
			try:
				# Check if it mcTrue
				regexp.search( objectType ).group( 'mc' )
				structure[name]['isMC'] = 1
			except AttributeError:
				structure[name]['isMC'] = 0
		#---- Method Used
		structure[name]['methodUsed'] = methodUsed

		return structure


	def __extract__(self, Dir, dictObjects, regexp):
		""".. method:: 	__extract__(dir, dictT, regexp) -> dict
	 	
		Recursive function to extract from a 'tag and probe' ROOT file all
		the relevant information. Returning a dictionary which stores all (TCanvas,
		RooFitResult,) RooDataSet (and RooPlot) with matches with regexp::

		  {# 'TCanvas': 
		   #           {'directory/subdirectory/.../nameOfTCanvas' : <ROOT.TCanvas object>,
		   #	     ...
		   #	     },
		   # 'RooFitResult' : 
		   #           { 'directory/subdirectory/.../nameOfRooFitResult': <ROOT.RooFitResult object>,
		   #	     ...
		   #           },
	 	    'RooDataSet':
		              { 'directory/subdirectory/.../nameOfRooDataSet': <ROOT.RooDataSet object>,
		              ...
		              },
		  }

		:param dir: root TDirectory (note TFile inherit from TDirectory) where to extract
		:type dir: ROOT.TDirectory
		:param dictT: directory where to store the information extracted 
		:type dictT: dict
		:param regexp: ?? (TO BE CHECKED)
		:type regexp: string

		:return: dictionary (see above)
		:rtype: dict

		:raise AttributeError: the root file is not an standard T&P

		.. warning:: 
		     
		   DEPRECATED TCanvas, RooFitResult and RooPlot storage
		            
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
			message = """The root file is not an standard T&P fit file""" 
			printError( self.__module__, message, AttributeError )
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
	# --- FIXME: To delete?
	def getCategory( self, name ):
		""".. method:: getCategory( name ) -> category

		Getter to extract the category belongs to some dataset

		:param name: the name of the dataset
		:type name: string

		:return: the category of the dataset
		:rtype: string
		"""
		try:
			return self.__attrDict__[name]['objectType']
		except KeyError:
			message = """The '%s' is not a fit_eff RooDataSet""" % name
			printWarning( self.__module__+'.getCategory', message )
			return None
	
	def getFitEffList( self ):
		""".. method:: getFitEffList() -> [ name1, ... ]

		Returns a strings list of the names of RooDataSet which are ``fit_eff``

		:return: list of dataset which ``methodUsed`` is ``fit_eff``
		:rtype: list of string
		"""
		fitEffList = []
		for name,Dict in filter( lambda (name,Dict): Dict['methodUsed'] == 'fit_eff' ,self.iteritems() ):
			fitEffList.append( name )
		
		if len(fitEffList) == 0:
			message = """There is no fit_eff RooDataSet in this file"""
			printWarning( self.__module+'.getFitEffList', message )
			return None

		return fitEffList
	
	def getCountMCName( self, name ):
		""".. method:: getCountMCName( name ) -> nameMCcountig

		Given the dataset name (fit_eff like), returns the name of its MC True counting equivalent.

		:param name: the dataname
		:type name: string

		:return: the name of its MC counting
		:rtype: string

		.. warning:: 
		   
		   To be revisited.. 

		"""
		try:
			return self[name]['refMC']['cnt_eff']
		except KeyError:
			message = """The is no counting MC True information associated with '%s' RooDataSet""" % name
			printWarning( self.__module__+'.getCountMCName', message )
	## Getters for attributes ######################################################################

	def write(self, fileOut):
		""".. method:: write( fileOut ) 

		Create a root file with all the RooDataSets and TH2F maps of 
		the instance.

		:param fileOut: name of the output root file
		:type fileOut: string

		:raise IOError: problems opening the file
		"""
		import os
		import ROOT

		f = ROOT.TFile(fileOut,'RECREATE')
		if f.IsZombie():
			message = 'Cannot open \'%s\' file. Check your permissions' % fileOut
			printError( self.__module__+'.write', message, IOError )
		
		howDatasets = 0
		for name,dataSet in self.RooDataSet.iteritems():
			dataSet.Write(name.replace('/','_'))
			try:
				for namehisto,histoTuple in self[name]['TH2F'].iteritems():
					for histo in histoTuple:
						#Watch out: not use the key name because we have 3 histos
						histo.Write('TH2F_'+histo.GetName().replace('/','_'))
						howDatasets += 1
			except KeyError:
				pass
		f.Close()
		
		#--- Check you have first the TH2F keys in your RooDataSet dict
		if howDatasets == 0:
			try:
				os.remove( fileOut )
			except IOError:
				#Why can't you remove something you have create =
				pass
			message = "Do not stored any TH2F map. You must use 'plotEffMap' method first."
			printWarning( self.__module__, message )


	def ls(self, className='RooDataSet'):
		""".. method:: ls( className='RooDataSet' ) 

		Print the identification of all the objects of type ``className``
		
		.. note:: 
		   
		   Probably will not need a argument as the others
		   attributes (RooPlot, TCanvas,...) are being deprecated.

		:param className: the kind of instance attribute
		:type className: string

		"""
		message = '='*20+' '+className+' '+'='*20+'\n'
		try:
			for name in self.__getattribute__(className).iterkeys():
				message += name+'\n'
		except AttributeError:
			message = """There's no attribute named '%s'!""" % className

		print message


	def plotEff1D( self, name, inputVarName, Lumi ):
		""".. method:: plotEff1D( dataname, variable, Lumi ) 
	
		Given a name directory-like for a ROOT.RooDataSet object,
	 	the function creates a 1-dim plot of 'variable_name' extracted 
		from the object and it will save it in a eps file. Also
		it will store the graph object creating a new key in the
		dataset dictionary::

		   self[nameRooDataSet]['tgraphs'] = { 'class_graph_name': TGraphAsymmErrors, ... }

		:param name: name of the dataset
		:type name: string
		:param variable: binned variable to use
		:type variable: string
		:param Lumi: luminosity
		:type Lumi: string

		:raise KeyError: the dataset is not in the root file (to be changed to NameError)
		:raise KeyError: the binned variable is not in the dataset

		"""
		#import rootlogon
		from tnputils import listTableEff,getEff, graphclassname
		from pytnp.steerplots.plotfunctions import plotAsymGraphXY

		dataset = None
		#-- Getting the class graph name
		_graphclassname = graphclassname( self, name )
		#-- Checking if the object exists
		try:
			dataset = self.RooDataSet[name]
		except KeyError:
		  	message = """you must introduce a valid name, '%s' is not a RooDataSet in the root file""" % name
			printError( self.__module__, message, KeyError )
		#--- Empty dataset
		if self.RooDataSet[name].numEntries() == 0:
			message = """Empty RooDataSet '%s'. Skipping...""" % name
			printWarning( self.__module__+'.plotEff1D',message)
			return None
		#--- Checking variable
		if not inputVarName in self[name]['binnedVar'].keys():
		  	message = """you must introduce a valid binned variable name, '%s' is not in the '%s' RooDataSet\n""" % (inputVarName,name )
			message += """The list of binned variables are '%s'""" % str(self[name]['binnedVar'].keys())  
			printError( self.__module__, message, KeyError )
		
		self[name]['tgraphs'] = { _graphclassname: {} }		
		# Special case: we have only one variable
		if len(self[name]['binnedVar']) == 1:
			graphName = self.resonance+'_'+self[name]['effType']+'_'+self[name]['objectType']+'_'+\
					self[name]['methodUsed']+'__'+inputVarName
                        if self[name]['isMC'] == 1:
				graphName += '__mcTrue'
			#--- Extracting the efficiency values per bin
			plotList = listTableEff( dataset )
			_min = 0
			_max = 0
			#--- Setting the points and extracting the min and max value
			#--- in order to build the frame to plot
			XPoints = []
			YPoints = []
			for varDict in plotList:  
				(eff,effLo,effHi) = varDict[self.effName]
				(var,varLo,varHi) = varDict[inputVarName]
				XPoints.append( (var, varLo, varHi) )
				YPoints.append( (eff, effLo, effHi) )

				_min = min( _min, varLo )
				_max = max( _max, varHi )
			#--- Cosmethics to storing the plot
			#title = self[name]['objectType']+' category'
			xtitle = self[name]['variables'][inputVarName]['latexName']+' '+self[name]['variables'][inputVarName]['unit']
			ytitle = 'efficiency'
			title = '  CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV  '

			self[name]['tgraphs'][_graphclassname][graphName] =  plotAsymGraphXY( XPoints, YPoints, xtitle, ytitle,\
						returnGraph=True, rangeFrame = (_min,0,_max,1.05), title=title, graphname=graphName ) 

			return 

		
		#-- More than one binned variable
		for varName in filter( lambda x: x != inputVarName, self[name]['binnedVar'].keys()):
                        _otherVarList_ = filter( lambda x: x != varName, self[name]['binnedVar'].keys() )
                        _otherVar_ = ''
                        for i in _otherVarList_:
                                _otherVar_ += i+', '
                        _otherVar_ = _otherVar_[:-2]
                        if len(_otherVar_ ) != 0:
                                _otherVar_ = ' in all the range of \'' +_otherVar_+'\''
			print '\033[1;34m'+name+': \''+varName+'\' bins'+_otherVar_+'\033[1;m'

                        #--- Extracting bins and array of bins
                        binsN = self[name]['variables'][varName]['binN']
                        arrayBins = self[name]['variables'][varName]['arrayBins']
                        for bin in xrange(binsN):
                                arrayBins = self[name]['variables'][varName]['arrayBins']
                                Lo = arrayBins[bin]
                                Hi = arrayBins[bin+1]
                                Central = (Hi+Lo)/2.0
				graphName = self.resonance+'_'+self[name]['effType']+'_'+self[name]['objectType']+'_'+\
						self[name]['methodUsed']+'__'+varName+'_bin'+str(bin)+'_'
                                #graphName = self.resonance+'_'+self[name]['methodUsed']+'_'+self[name]['effType']+'_'+\
                                #                self[name]['objectType']+'__'+varName+'_bin'+str(bin)+'_'
                                #Getting list of efficiency values plus variables
                                _plotList = eval('getEff(dataset,self.effName,'+varName+'='+str(Central)+')')
                                #print _plotList
                                #Extracting info to plot
				#try:
                                (eff,effErrorLo,effErrorHi),otherVarDict = _plotList[0]

                                if len(filter( lambda (eff,__dic): eff[0] == 0.0, _plotList )) == len(_plotList):
					printWarning( self.__module__+'.plotEff1D',"Skipping... Efficiencies in the dataset not calculated")
                                        continue
                                _max = {}
                                _min = {}
				varPoints = {}
				effPoints = {}
                                for otherVarName, val in otherVarDict.iteritems():
					varPoints[otherVarName] = []
					effPoints[otherVarName] = []					
                                        _max[otherVarName] = 0.0
                                        _min[otherVarName] = 0.0
                                for (eff,effLo,effHi),otherVarDict in _plotList:
                                        for otherVarName, (central, low, high) in otherVarDict.iteritems():
                                                _min[otherVarName] = min( _min[otherVarName], low )
                                                _max[otherVarName] = max( _max[otherVarName], high )
						varPoints[otherVarName].append( (central,low,high) ) 
						effPoints[otherVarName].append( (eff, effLo, effHi) )

                                title = self.resLatex+', ('+str(Lo)+','+str(Hi)+') '+self[name]['variables'][varName]['latexName']+' range, '
                                title += self[name]['objectType']+' category'
                                for otherVarName, (central, low, high) in otherVarDict.iteritems():
					graphname = graphName+otherVarName
					if self[name]['isMC'] == 1:
						graphname += '__mcTrue'
					xtitle = self[name]['variables'][otherVarName]['latexName']+\
							' '+self[name]['variables'][otherVarName]['unit']
					ytitle = 'efficiency'
					title = 'CMS Preliminary,'+Lumi+' #sqrt{s}=7 TeV'
					ranges = (_min[otherVarName],0,_max[otherVarName],1.05)
					self[name]['tgraphs'][_graphclassname][graphname] = plotAsymGraphXY( varPoints[otherVarName], effPoints[otherVarName],\
							xtitle, ytitle, returnGraph=True, rangeFrame=ranges, title=title, graphname=graphname)


	
	def plotEffMap( self, name, x, y, Lumi, **keywords ):
		""".. method:: plotEff2D( name, varX, varY, Lumi ) 

		Giving a RooDataSet name in directory-like format,
		the function will do a bi-dimensional plot of 
		efficiency with ``varX`` and ``varY`` variables. Also, it
		will stores the graph within the dataset dictionary
		
		:param name: name of the dataset
		:type name: string
		:param varX: binned variable to be used in the x-axis
		:type varX: string
		:param varY:  binned variable to be used in the y-axis
		:type varY: string
		:param Lumi: luminosity
		:type Lumi: string

		:raise KeyError: the dataset is not in the root file (to be changed to NameError)
		:raise KeyError: some binned variables is not in the dataset

		"""
		import ROOT
		ROOT.gROOT.SetBatch(1)
		import pytnp.steerplots.rootlogon
		from tnputils import getBinning,listTableEff,getEff

		#FIXME: Meter los errores en la misma linea (ahora te salta
		#       de linea (TEXT option)
		try:
			dataSet = self.RooDataSet[name]
		except KeyError:
			message = """There is no RooDataSet with name '%s'""" % name
			printError( self.__module__+'.plotEfMap', message, AttributeError )
		#-- Are the variables in the RooDataSet?
		varNotInDatasetList = filter( lambda var:  not var in self[name]['binnedVar'].keys(), [x, y] )
		if len(varNotInDatasetList) != 0:
			message = 'No binned variable: '
			for var in varNotInDatasetList:
				message += "'%s' " % var
			message += "in the RooDataSet '%s'. Skipping plot generation..." % name
			printWarning( self.__module__+'.plotEffMap', message )
			# --- Skipping plot generation
			return 
		
		#--- Name for the histo and for the plot file to be saved
		histoName = 'TH2F_'+name
		#--- Checking if the histo is already stored and plotted
		if self[name].has_key('TH2'):  #### FIXME: has_key o has_attribute ???
			#-- Skipping, work it's done!
			return None
		#---- Preparing all the stuff
		title = self.resLatex+', '+self[name]['objectType']+' '+self[name]['effType']+' '+dataSet.GetTitle()
		yNbins = self[name]['variables'][y]['binN']
		#arrayBinsY = self[name]['variables'][y]['arrayBins']---> # I need the PyDoubleBuffer
		#------------------------------------------
		__argSet__ = dataSet.get()
		dum, arrayBinsY = getBinning( __argSet__[y] )
		#------------------------------------------
		xNbins = self[name]['variables'][x]['binN']
		#arrayBinsX = self[name]['variables'][x]['arrayBins']---> # I need the PyDoubleBuffer
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
		_listTableEffList = listTableEff(self.RooDataSet[name])
		#skipPoints = False
		for binDict in _listTableEffList:
			#-- Extract error values
			#if abs(binDict[self[name]['eff']][0]-self.badPoint[0]) < 1e-9:
			#	skipPoints = True
			#	continue
			b = h.FindBin( binDict[x][0] , binDict[y][0] )
			h.SetBinContent(b, binDict[self[name]['eff']][0])
			h.SetBinError(b, (binDict[self[name]['eff']][2]-binDict[self[name]['eff']][1])/2.0 ) # WATCH: Error 'Simetrized' 
			hlo.SetBinContent(b, binDict[self[name]['eff']][1])
			hhi.SetBinContent(b, binDict[self[name]['eff']][2])
		c = ROOT.TCanvas()
		#c.SetLogy(isLog[1]) 
		h.GetYaxis().SetTitle(self[name]['variables'][y]['latexName'])
		h.GetXaxis().SetTitle(self[name]['variables'][x]['latexName'])
		h.GetZaxis().SetTitle(self[name]['variables'][self[name]['eff']]['latexName'])
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

	#	if skipPoints:
	#		message = '\033[1;33mplotEff2D Warning: Some efficiencies points are failed in the fit, the last plot will skip '\
	#                         'values with %.4f\033[1;m' % self.badPoint[0]
	#		print message

		#FIXME: attribute o llave del diccionario del rootdataset??
		try:
			self[name]['TH2'][histoName] = (h, hlo, hhi)
		except KeyError:
			self[name]['TH2F']  = {} 
			self[name]['TH2F'][histoName] = (h, hlo, hhi)


