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
	resonanceLatex = ''
	nameDict = { 'JPsi' : ('J/#Psi','JPsi'),
			'Upsilon': ('All #Upsilon','AllUpsilons'),
			'Z' : ('Z#rightarrow#mu#mu','Z'),
			'DATA' : (' Data', '_DATA')
			}
	try:
		num = regexp.search( aFile ).group( 'NUMBER' )
		resonanceLatex = '#Upsilon('+num+')'
		resonance = 'Upsilon'+num

	except AttributeError:
		#Reverse sorted to assure DATA is the last one
		for name, (resLatex,res) in sorted(nameDict.iteritems(),reverse=True):
			if aFile.find( name ) != -1:
				#Watch: we are including _DATA case
				resonanceLatex += resLatex
				resonance += res
		if resonance == '':
			message ="""\033[1;31mgetResName: 
		WARNING: This function is highly dependent of the 
		name of the file, you need an standard format like:
		NameOFResonance_X_blabla.root

		Unrecognized name: \033[1;m\033[1;33m  %s\033[1;m""" % aFile
			print message
			return None
		
	except:
		message ="""\033[1;31mgetResName: 
		ERROR: Something wrong!! Check the code pytnp.getResName
		because this is an unexpected error\033[1;m"""
		print message
		exit(-1)

	return resonance,resonanceLatex

def getEff( dataSet, **keywords):
	"""
	getEff(RooDataSet, var1=value, ...) --> eff, effErrorLow, effErrorHigh                
	                                    --> eff, effErrorLow, effErrorHigh, dictionary

	Giving a binned variables returns the efficiency which 
	corresponds to those values. There is 2 output signatures 
	depending of the argument variables introduced; if the 
	variables are the exhausted set of the RooDataSet, the output
	will be a tuple of efficiency (CASE 1). Otherwise if the
	input variables don't cover all the RooDataSet binned 
	variables, the output will be the efficiency tuple plus
	a dictionary which the names of the resting variables as keys
	and the tuples of their bin values as values (CASE 2).
	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataSet )
	#---  All the binned variables in the dataset
	datasetVarList = filter( lambda x: x.lower().find('eff') == -1, _swapDict.iterkeys() )
	effList = filter( lambda x: x.lower().find('eff') != -1, _swapDict.iterkeys() )
	#---- Sanity check
	if len(effList) != 1:
		message ="""\033[1;31mpytnp.getEff ERROR: Unexpected Error!! It seems that in %s there is no
efficiency variable...\033[1;m""" % dataSet.GetName()
		print message
		raise 
	effName = effList[0]

	varList = []
	nameVarList = []
	for var,value in keywords.iteritems():
		if not var in datasetVarList:
			message ="""\033[1;31mpytnp.getEff ERROR: %s is not a binned variable of the dataset %s\033[1;m""" % (var,dataSet.GetName())
			print message
			raise KeyError
		varList.append( (var,value) )
		nameVarList.append( var )
	#---- Sanity check
	if len(varList) != 1:
		message ="""\033[1;31mpytnp.getEff ERROR: You must introduce at least one variable\033[1;m"""
		print message
		print 'Usage:\n',getEff.__doc__
		raise 
	#--- Variables the user don't ask. This is the case when the user
	#--- wants a list of efficiency given a fixed value of one variable
	noAskVar = filter( lambda x: x not in nameVarList, datasetVarList )
	listReturn = False
	effVarList = None
	if len(noAskVar) != 0:
		listReturn = True
		effVarList = []
	#---- Sanity check
	if len( varList ) > len(datasetVarList):#FIXME---> can be more than 2 variables...
		message ="""\033[1;31mpytnp.getEff ERROR: You are using more variables than in dataset %s\033[1;m""" % dataSet.GetName()
		print message
		raise

	#-- Get the table of efficiencies
	tableList = tableEff( dataSet ) 

	for valDict in tableList:
		#--  From the list of the variables we want the efficiencies (varList), put the value inside  
		#--- of the ranges (valDict[var][1:][i]) in the list 
		fList = filter( lambda (var,value): valDict[var][1:][0] <= value and valDict[var][1:][1] > value , varList )
		#--  If our variables are all the variables available, we have 1-to-1 correspondence
		#--- with a efficiency value-> return this value
		if not listReturn and len(fList) == len( varList ):
			return valDict[effName]
		#--  If our variables are less than the variables available, we're going to return
		#--- a list with the (restOfvariables,efficiencies) in order to recover the 1-to-1 correspondence
		elif listReturn and len(fList) != 0:
			restVarDict = dict( [ (_name, valDict[_name]) for _name in noAskVar ] )
			effVarList.append( (valDict[effName],restVarDict) )

	if listReturn and len(effVarList) > 0 :
		#--output: (tuple,dict) where tuple is efficiency values and dict have the
		#--- names of the variables as keys and tuple as values  
		return effVarList

#------- OLD VERSION: pt, eta hardcoded
#	for valDict in tableList:
#		#-- Extract ranges
#		ptRanges = valDict['pt'][1:]
#		etaRanges = valDict['eta'][1:]
#		if ( ptRanges[0] <= pt and ptRanges[1] >= pt ) and \
#				( etaRanges[0] <= eta and etaRanges[1] >= eta ):
#					return valDict['eff']
	message = '\033[1;34mpytnp.getEff Info: There is no bin where live '
	for var,val in varList:
		message += var+'='+str(val)+', '
	message = message[:-2]+'\033[1;m'
	print message

	return None
				
def getBinning( var ):
	"""
	getBinning( ROOT.RooArgVar ) -> bins, arrayBins

	Giving a RooArgVar, the function returns 
	how many bins the variable has and an array (of doubles)
	with with his values.

	WARNING: Use with caution. The doubles array are
	         potentially dangerous.
	"""

	binsN = var.numBins()
	binning = var.getBinning()
	arrayBins = binning.array()
	#-- By default arrayBins have a lot of space, so usign SetSize
	#---- to resize the array
	#---- The number of elements = bins+1 (remember edges)
	arrayBins.SetSize(binsN+1)

	return binsN, arrayBins

#FIXME: Un-hardcode pt, eta
def tableLatex(dataset):
	"""

	Giving a RooDataSet, the function returns a table in latex
	format 
	"""
	#Getting table
	effList = tableEff(dataset)
	##Getting how many eta and pt bins we have
	etaBins = set([ (i['eta'][1],i['eta'][2]) for i in effList] )
	etaBins = sorted(list(etaBins))
	etaNbins = len(etaBins)
	ptBins  = set([ (i['pt'][1],i['pt'][2]) for i in effList] )
	ptBins  = sorted(list(ptBins)) 
	ptNbins = len(ptBins)
	#Some usefuls function
	edges = lambda x,y: '(%0.1f, %0.1f)' % (x,y) 
	effsetter = lambda eff,lo,hi: '$%.3f\\pm^{%.3f}_{%.3f}$ & ' % (eff,hi,-lo) 
	central = lambda low,high: (high+low)/2.0

	toLatex = '\\begin{tabular}{c'
	#Number of columns
	toLatex += 'c'*etaNbins+'}\\toprule\n'
	#header
	toLatex += '$p_T^\\mu({\\rm GeV})$ {\\boldmath$\\backslash$}$\\eta^\\mu$  & '
	for low,high in etaBins:
		toLatex += edges(low,high)+' & '
	toLatex = toLatex[:-2]+'\\\\ \\midrule\n'
	#Filling the table
	for lowPt,highPt in ptBins:
		toLatex += edges(lowPt,highPt)+' & '
		for lowEta,highEta in etaBins:
			try:
				eff,effErrorLow,effErrorHig,effErr = getEff(dataset,central(lowPt,highPt),central(lowEta,highEta))
			#Empty bin
			except TypeError:
				toLatex += ' & '
			toLatex += effsetter(eff,effErrorLow,effErrorHig)
		toLatex = toLatex[:-2]+'\\\\\n'
	toLatex += ' \\bottomrule\n'
    	toLatex += '\\end{tabular}'

	print toLatex
	return toLatex

	
def tableEff(dataSet):
	"""
	tableEff( dataSet ) --> tableList

	Giving a RooDataSet, the function returns a list where every 
	element is an entry of the RooDataSet stored as a dictionary:
	For every entry we have
	                { 'var1':  (pt, minimum pt bin, maximum pt bin),
	                  'var2': (eta, minimum eta bin, maximum eta bin),
			   ...
			  'nameEfficiency': (eff, error low, error high, error)
			}

	"""
	#---- Checking the variables in dataset
	_swapDict = getVarInfo( dataSet )
	datasetVarList = [ i for i in _swapDict.iterkeys() ]
	try:
		argSet = dataSet.get()
	except AttributeError:
		print '\033[1;31mpytnp.tableEff Error: '+str(dataSet)+' is not a RooDataSet\n\033[1;m'
		raise AttributeError

	varDict = dict( [ ( varName, argSet[varName]) for varName in datasetVarList ] )
	valList= []
	for i in xrange(dataSet.numEntries()):
		dataSet.get(i)
		# Watch: for binned variables Hi and Lo is the limit of the bin
		#        for efficiencies. is the asymmetric error
		valList.append( dict( [ (varName,(argset.getVal(), argset.getVal()+argset.getErrorLo(),\
				argset.getVal()+argset.getErrorHi()) ) for varName,argset in varDict.iteritems() ] ) )
	return valList


def getVarInfo( dataset ):
	"""
	getDataSetVar( RooDataSet ) -> { 'var1': { 'latexName': 'blaba', 'unit': 'unit' },
					 ... 
				       }
	"""
	#TODO: Diccionario con valore s bonitos de pt, eta, etc...
	#FIXME: Control de errores
	varinfo = {}

	try:
		arg = dataset.get()
	except AttributeError:
		message = '\033[1;31mgetVarInfo: The object %s is not a RooDataSet\033[1;m' % str(dataset)
		print message
		raise KeyError
	#-- Get the list with the name of the variables
	varList = arg.contentsString().split(',')
	for name in varList:
		if isinstance(arg[name],ROOT.RooCategory):
			continue
		binN, arrayBin = getBinning( arg[name] )
		varinfo[name] = { 'unit': arg[name].getUnit(), 'latexName': arg[name].getTitle().Data(), \
				'binN' : binN, 'arrayBins': arrayBin 
				} #Nota some TString instance--> normalizing to str with Data method

	effName = filter( lambda x: x.lower().find('eff') != -1, [i for i in varinfo.iterkeys()] )[0]
	varinfo[effName]['latexName'] = '#varepsilon'

	return varinfo

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
	#-- Binned variables (efficiencies are calculated respect to)
	x = None
	y = None
	eff = None
	def __init__(self, filerootName, **keywords):
		"""
                pytnp(filerootName, resonance=('name','nameLatex'), dataset='type', mcTrue=true ) -> pytnp object instance

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

		TODO: Put dictionary output
		"""
		#--- Checking the keys dictionary passed ----#
		#--- Keys valid
		valid_keys = ['resonance', 'dataset', 'mcTrue','variables']
		#---- Some initializations using user inputs ---#
		dataset = ''
		for i in keywords.keys():
			if not i in valid_keys:
				message = '\033[1;31mpytnp: invalid instance of pytnp: you can not use %s as key argument, ' % i
				message += ' key arguments valids are \'resonance\', \'dataset\', \'mcTrue\', \'variables\' \033[1;m' 
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
			elif i == 'dataset':
				dataset = keywords['dataset']
			elif i == 'variables':
				#-- Sanity checks
				if len(i) != 2:
					message ='\033[1;31mpytnp: Not valid variables=%s key; must be a tuple containing 2 elements\033[1;m'
					print message
					raise KeyError
				self.x = i[0]
				self.y = i[1]

                #--------------------------------------------#
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
		#--- Extract all the objects of the rootfile
		self.__dict__ = self.__extract__(fileroot, self.__dict__, dataset) 
		print ''
		
		#--- Getting the variables names of the RooDataSet 
		#----- (By construction in CMSSW package all the RooDataSet
		#------ should contain the same variables)
		for dataset in self.__dict__['RooDataSet'].itervalues(): 
			self.variables = getVarInfo(dataset) 
			#break -> In principle all dataset must contain the same variables
		
		#------ Setting the binned Variables: extract efficiencies from last list
		self.binnedVar = filter( lambda x: x.lower().find('eff') == -1, self.variables ) 
		self.eff = filter( lambda x: x.lower().find('eff') != -1, self.variables )[0]
		#------ Check the variables introduced by user are there, and put in
		if self.x and self.y:
			message = """\033[1;33mWarning: Variable %s is not in the root file, using %s and %s"""
			if not self.x in self.binnedVar:
				#FIXME: Que pasa si solo tengo una variable???
				message = message % (self.x,self.binnedVar[0],self.binnedVar[1])
				print message
				self.x = self.binnedVar[0]
			elif not self.y in self.binnedVar:
				message = message % (self.x,self.binnedVar[0],self.binnedVar[1])
				print message
				self.y = self.binnedVar[1]
		else:
			self.x = self.binnedVar[0]
			self.y = self.binnedVar[1]

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
		#--- We are not interested about the MC, only in cnt and fit_eff
		map( lambda (Name,Dumm): self.__attrDict__.pop(Name), mcTrueData )
		#--- We are not instested about the sbs and cnt not MC
		map( lambda y: self.__attrDict__.pop( y[0] ), filter( lambda x: x[1]['isMC'] == 0 and x[1]['methodUsed'] != 'fit_eff',\
				self.__attrDict__.iteritems() ) ) 
		_prov = set()
		#--- The dictionary itself contains only the RooDataSets
		for name, dataSet in self.__dict__['RooDataSet'].iteritems():
			#Warning this change is potentially dangerous, may leave some parts 
			#inuseful
			#self[name] = dataSet
			try:
				self[name] = self.__attrDict__[name]
			# To get also the no fit_eff --> Am I sure?? TODO: to be Checked
			except KeyError:
				self[name] = self.__getType__(name,{})[name]
			self[name]['dataset'] = dataSet
			#self[name]['variables'] = getVarInfo(dataSet)
			#self[name]['ArgSet']
			#--To store the categories we have
			_prov.add( self[name]['objectType'] )
		#-- Storing the categories we have 
		self.categories = list(_prov)
		#-- In case don't introduce binned variables--> default
		if len( filter( lambda x: x == 'variables', keywords.keys()) ) == 0:
				try:
					message = """\033[1;34mpytnp: you have not introduced any binned variables, I will use '%s' and '%s'\033[1;m""" % \
							( self.binnedVar[0], self.binnedVar[1] )
					print message
				except IndexError:
					message = """\033[1;31mpytnp: Unexpected error! I only found one variable: %s. Exiting...""" % str(self.binnedVar)
					print message
					raise IndexError

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
			print message
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

###############################################################################################################
###################### FIXME :  DEPRECATED, to be removed #####################################################
###############################################################################################################
#	def inferInfo( self, name ):
#		"""
#		inferInfo( name ) -> str
#
#		Giving a standard directory-like name of an object,
#		the function returns what kind of efficiency is,
#		MuonID or Trigger.
#		"""
#		#TODO: Si mantegno __attrDict__ se puede extraer
#		#      de ese diccionario dicrectamente
#		info = name.split('/')
#		toReturn = ''
#		if len(info) != 1:
#			toReturn = info[1].split('_')[0]
#			if info[0] == 'histoMuFromTk':
#				toReturn += ' MuonID'
#			elif info[0] == 'histoTrigger':
#				### ---- FIXED---------------------------------------
#				### There is no underscore, change it in tnp Producer
#				### Neither if is Global or tracker
#				#toReturn = info[1].split('pt')[0]
#				### -------------------------------------------------
#				toReturn += ' Trigger'
#	
#		return toReturn
###############################################################################################################
###################### FIXME :  DEPRECATED, to be removed #####################################################
###############################################################################################################
#	def searchRange( self, name ):
#		"""
#		searchRange(name) -> 'range'
#
#		Getting a directory-like name of a RooPlot
#		extracts which's the range of the hidden 
#		variable. It uses the directory-like notation
#		to find which datased was used to generate the
#		plot:
#		RooPlot    -->  histoMuFromTk/Glb_pt_eta_mcTrue/fit_eff_plots/eta_plot__pt_bin10__mcTrue_true
#		RooDataSet -->  histoMuFromTk/Glb_pt_eta_mcTrue/fit_eff
#		"""
#		#-- Getting the dataset name
#		sName = name.split('_plots/')
#		dataSet = None
#		try:
#			dataSet = self.RooDataSet[ sName[0] ]
#		except KeyError:
#			message = """
#ERROR: What the f***!! This is an expected error... Exiting
#                        """
#			exit()
#		#-- var1_plot__var2_binX[__something_else]
#		#-- var1 is the plotted variable, var2 is the hidden
#		#   variable and could be something labels, but doesn't
#		#   matter to us
#		try:
#			Var = sName[1].split('__')
#			plotVar = Var[0].split('_plot')
#			hidVar = Var[1].split('_')[0]
#		#The TCanvas version
#		except IndexError:
#			Var = sName[1].split('_PLOT_')
#			plotVar = Var[0]
#			hidVar = Var[1].split('_')[0]
#		try:
#			nBin = int(Var[1].split('_bin')[1])
#		#To deal with the new marvelous notation for Trigger
#		except ValueError:
#			swap = Var[1].split('_bin')[1]
#			nBin = int(swap.split('_')[0])
#		######---Hay otra forma mas facil: 
#		#hidVar = self.RootPlot[name].GetTitle()
#		# Devuelve 'variable_binX'
#		argSet = dataSet.get()
#		# FIXME
#		#-- WARNING! If hidVar doesn't exist
#		#   the program will crash when trying
#		#   to retrieve the variable. I can't
#		#   found a secure method to extract it.
#		v = argSet[hidVar]
#		bins, arrayBins = getBinning( v )
#		rangeStr = hidVar+' range '
#		rangeStr += '('+str(arrayBins[nBin])+','+str(arrayBins[nBin+1])+')'
#
#		return rangeStr
		
	#FIXME: Nota que la funcio no te gaire sentit per mes de dos variables
	#TODO:  Extract the failed fit value 
	def plotEff1D( self, name ):
		"""
		plotEff1D( RooDataSet ) -> ROOT.RooHist
	
		Given a name directory-like for a ROOT.RooDataSet object,
	 	the function creates a 1-dim plot etracted from the
		object and it will save it in a eps file. Also
		it will store in the dictionary of the instance if
		the object does not exist.
		"""
		#-- Checking if the object exists
		if not self.RooDataSet.has_key(name):
			# So, skipping the action.. it's done
			message = """\033[1;34mpytnp.plotEff1D: there is no RooDataSet with name %s\033[1;m""" % name
			print message
			return None
		#--- Title from name: name must be 
		#--- in standard directory-like name
		title = None #self.resLatex+' '+self.inferInfo(name)+', '+self.searchRange(name)
		dataset = None
		try:
			dataset = self.RooDataSet[name]
		except KeyError:
		  	print """\033[1;33mpytnp.plotEff1D Error: you must introduce a valid name, %s is not a RooDataSet in the root file\033[1;m""" % name
			print plotEff1D.__doc__
			raise KeyError
		
		#histo = None
		#For all var1 bin, get eff respect var2
		for varName in self.binnedVar:
			binsN = self.variables[varName]['binN']
			arrayBins = self.variables[varName]['arrayBins']
			_otherVarList_ = filter( lambda x: x != varName, self.binnedVar )
			_otherVar_ = ''
			for i in _otherVarList_:
				_otherVar_ += i+', '
			_otherVar_ = _otherVar_[:-2]	
			print '\033[1;34mPlotting \''+varName+'\' bins in all the range of '+_otherVar_+'\033[1;m'
			for bin in xrange(binsN):
				Lo = arrayBins[bin]
				Hi = arrayBins[bin+1]
				title = self.resLatex+', ('+str(Lo)+','+str(Hi)+') '+self.variables[varName]['latexName']+' range'
				graphName = self[name]['methodUsed']+'_'+self[name]['effType']+'_'+\
						self[name]['objectType']+'__'+varName+'_bin'+str(bin)+'_' 
				#Getting list of efficiency values plus variables 
				Central = (Hi+Lo)/2.0
				_plotList = eval('getEff(dataset,'+varName+'='+str(Central)+')')
				#Extracting info to plot
				(eff,effErrorLo,effErrorHi),otherVarDict = _plotList[0] #FIXME:Control de errores?!
				graph = {}
				_max = {}
				_min = {}
				for otherVarName, val in otherVarDict.iteritems():
					graphName = graphName+otherVarName 
					graph[otherVarName] = ROOT.TGraphAsymmErrors()
					graph[otherVarName].SetName( graphName )
					graph[otherVarName].SetMarkerSize(1)
					_max[otherVarName] = 0.0
					_min[otherVarName] = 0.0
				entry = 0
				for (eff,effErrorLo,effErrorHi),otherVarDict in _plotList: 
					for otherVarName, (central, low, high) in otherVarDict.iteritems():
						_min[otherVarName] = min( _min[otherVarName], low )
						_max[otherVarName] = max( _max[otherVarName], high )
						graph[otherVarName].SetPoint(entry, central, eff )
						graph[otherVarName].SetPointEXlow( entry, central-low )
						graph[otherVarName].SetPointEXhigh( entry, high-central) 
						graph[otherVarName].SetPointEYlow( entry, eff-effErrorLo )
						graph[otherVarName].SetPointEYhigh( entry, effErrorHi-eff )
					entry += 1
				#-- Nota que ya tienes definido otherVar unas lineas mas arriba
				for otherVarName, (central, low, high) in otherVarDict.iteritems():
					c = ROOT.TCanvas()
					frame = c.DrawFrame(_min[otherVarName],0,_max[otherVarName],1.05)
					frame.SetName( 'frame_'+graphName )
					frame.SetTitle( title )
					frame.GetXaxis().SetTitle(self.variables[otherVarName]['latexName']+' '+self.variables[otherVarName]['unit'])
					frame.GetYaxis().SetTitle( '#varepsilon' )
					frame.Draw()
					graph[otherVarName].Draw('P')
					c.SaveAs( graph[otherVarName].GetName()+'.eps' ) 
					c.Close()

		
#---------------OLD VERSION--> It doesn't work for the lastest CMSSW TnP packages
#		#--- Graph, getHist returns a RooHist which inherits from
#		#--- TGraphErrorAsym
#		ymin = 0
#		#ymin = h.GetYaxis().GetBinLowEdge(1) #Solo tiene un bin?
#		#if ymin < 0:
#		#	ymin = 0
#		#	ymax = h.GetYaxis().GetBinUpEdge( h.GetYaxis().GetNbins() )
#		ymax = 1.0
#		xmin = h.GetXaxis().GetBinLowEdge(1) #Solo tiene un bin, es un TGraph
#		xmax = h.GetXaxis().GetBinUpEdge( h.GetXaxis().GetNbins() )
#		#Make canvas
#		c = ROOT.TCanvas()
#		frame = c.DrawFrame(xmin,ymin,xmax,ymax)
#		# Preparing to plot, setting variables, etc..
#		frame.SetTitle( title )
#		h.SetTitle( title )  #To Store the info
#		if varUnit != '':
#			xlabel += '('+varUnit+')'
#		frame.GetXaxis().SetTitle( xlabel ) 
#		h.GetXaxis().SetTitle( xlabel )
#		frame.GetYaxis().SetTitle( 'Efficiency' )
#		h.GetYaxis().SetTitle( 'Efficiency' )
#		h.Draw('P')
#		c.SaveAs(self.resonance+'_'+histoName.replace('/','_')+'.eps')
#		c.Close()
#		del c
#		#--- Storing the histo
#		self[histoName] = h
#------------------------------------------------------------------------------------------

	
	def plotEff2D( self, name, **keywords ):
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
		arrayBinsY = self.variables[y]['arrayBins']
		xNbins = self.variables[x]['binN']
		arrayBinsX = self.variables[x]['arrayBins']
		hTitleOfHist = name.replace('/','_')
		h = ROOT.TH2F( hTitleOfHist, '', xNbins, arrayBinsX, yNbins, arrayBinsY )
	  	hlo = h.Clone("eff_lo")
		hlo.SetName( 'low_'+hTitleOfHist )
		hhi = h.Clone("eff_hi")
		hhi.SetName( 'high_'+hTitleOfHist )
		#-- Getting the efficiencies
		_tableEffList = tableEff(self.RooDataSet[name])
		for binDict in _tableEffList:
			b = h.FindBin( binDict[x][0] , binDict[y][0] )
			h.SetBinContent(b, binDict[self.eff][0])
			h.SetBinError(b, (-binDict[self.eff][1]+binDict[self.eff][2])/2.0 ) # WATCH: Error 'Simetrized' 
			hlo.SetBinContent(b, binDict[self.eff][1])
			hhi.SetBinContent(b, binDict[self.eff][2])
		c = ROOT.TCanvas()
		#c.SetLogy(isLog[1]) 
		h.GetYaxis().SetTitle(self.variables[y]['latexName'])
		h.GetXaxis().SetTitle(self.variables[x]['latexName'])
		h.GetZaxis().SetTitle(self.variables[self.eff]['latexName'])
		h.SetTitle( title )
		h.Draw('COLZ')
		htext = h.Clone('htext')
		htext.SetMarkerSize(1.0)
		htext.SetMarkerColor(1)
		#if isLog[1]:
		#	ROOT.gStyle.SetPaintTextFormat("1.2f")
		#	htext.Draw('ESAMETEXT0')
		#else:
		ROOT.gStyle.SetPaintTextFormat("1.3f")
		htext.Draw('SAMETEXT0')
		#plotName = self.resonance+'_'+name.replace('/','_')+isLog[0]+'.eps'
		plotName = self.resonance+'_'+name.replace('/','_')+'.eps'
		c.SaveAs(plotName)

		#FIXME: Ponerlo en el diccionario del RooDataSEt
		try:
		
			self.TH2F[histoName] = (h, hlo, hhi)
		except AttributeError:
			self.__setattr__('TH2F',{}) 
			self.TH2F[histoName] = (h, hlo, hhi)

#---------------OLD VERSION--> DEPRECATED.  To be removed
##		argSet = dataSet.get()
##	  	pt = argSet['pt'];
##	        eta = argSet['eta'];
##	        eff = argSet['efficiency'];
#		# Este metodo no me gusta... lo hago a mana
#		#h = dataSet.createHistogram(eta, pt)
#		##### Creacion histograma
#		##-- Bineado 
#		ptNbins, arrayBinsPt = getBinning( pt )
#		etaNbins, arrayBinsEta = getBinning( eta )
#		#-- To avoid warning in pyROOT
#		hTitleOfHist = name.replace('/','_')
#		h = ROOT.TH2F( hTitleOfHist, '', etaNbins, arrayBinsEta, ptNbins, arrayBinsPt )
#		#h.SetTitle( title )
#		#h = ROOT.TH2F( 'h', '', ptNbins, arrayBinsPt, etaNbins, arrayBinsEta )
#	  	hlo = h.Clone("eff_lo")
#		hlo.SetName( 'low_'+hTitleOfHist )
#		hhi = h.Clone("eff_hi")
#		hhi.SetName( 'high_'+hTitleOfHist )
#		
#		# To control the case where we don't have entries
#		# If we don't have entries, b will be None
#		b = None
#		for i in xrange(dataSet.numEntries()):
#			_dummy = dataSet.get(i)
#			b = h.FindBin(eta.getVal(), pt.getVal())
#			h.SetBinContent(b, eff.getVal())
#			h.SetBinError(b, (-eff.getErrorLo()+eff.getErrorHi())/2.0) # WATCH: Error 'Simetrized' 
#			hlo.SetBinContent(b, eff.getVal()+eff.getErrorLo())
#			hhi.SetBinContent(b, eff.getVal()+eff.getErrorHi())
##			print 'bin=',b,' pt =', pt.getVal(),' eta=',eta.getVal()
#		if b:
#			#Si es plot --> Entra un histo, graph o lo que sea, de momento
#			#Lo dejo asi, pero hay que cambiarlo
#			for isLog in [ ('',0), ('_log',1) ]:
#				c = ROOT.TCanvas()
#				c.SetLogy(isLog[1]) 
#				h.GetYaxis().SetTitle('p_{t} (GeV/c)')
#				h.GetXaxis().SetTitle('#eta')
#				h.GetZaxis().SetTitle('eff')
#				h.SetTitle( title )
#				h.Draw('COLZ')
#				htext = h.Clone('htext')
#				htext.SetMarkerSize(1.0)
#				htext.SetMarkerColor(1)
#				if isLog[1]:
#					ROOT.gStyle.SetPaintTextFormat("1.2f")
#					htext.Draw('ESAMETEXT0')
#				else:
#					ROOT.gStyle.SetPaintTextFormat("1.3f")
#					htext.Draw('SAMETEXT0')
#				plotName = self.resonance+'_'+name.replace('/','_')+isLog[0]+'.eps'
#				c.SaveAs(plotName)
#			#-- Storing the histo
#			try:
#				self.TH2F[histoName] = (h, hlo, hhi)
#			except AttributeError:
#				self.__setattr__('TH2F',{}) 
#				self.TH2F[histoName] = (h, hlo, hhi)


