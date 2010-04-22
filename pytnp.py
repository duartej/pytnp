"""
"""
import ROOT

#--- TODO: vale la pena que herede de un diccionario??
#--------- Se podira crear la llave del diccionario que
# es el propio objeto dinamicamente, i.e que vaya cambiando
# las llaves segun estemos en un directorio o en otro...

class pytnp(dict):
	"""
	Class to retrieve the Tag and Probe root file generated with the fit

	"""
	counter = 0
	__fileroot__ = None
	def __init__(self,filerootName):
		"""
                pytnp(fileroot)
		"""
		classNames = ['TCanvas','RooDataSet','RooPlot','RooFitResult']
		fileroot = ROOT.TFile(filerootName)
		#self.__rootfile__ = fileroot
		#__dict__ 
		print 'Extracting info from '+filerootName+' .',
		self.__dict__ = {}
		self.__dict__ = self.__extract__(fileroot,self.__dict__) 
		print ''
		self.__fileroot__ = fileroot
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

	def __extract__(self,Dir,dictObjects = {}):
	 	"""
	 	extract(ROOT.TDirectory Dir, python dict) -> dict
	 	
	 	Dictionary which stores all the relevant info from pytnp class, i.e TCanvas
		RooFitResult, RooDataSet and RooPlot:
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
	 	#Python --> _dirSave is a reference to ROOT.gDirectory, so whenever gDirectory changes, _dirSaves changes too
	 	#           I can't use the gDirectory
	 	#_dirSave = ROOT.gDirectory
	 	_dirSave = Dir
		#Storing the father->child info
		#__hierarchy__ = []
	 	for key in Dir.GetListOfKeys():
	 		className = key.GetClassName()
	 		if key.IsFolder():
	 			##-- Extracting the Folder from Dir
				#if key.ClassName() != 'TFile':
				#	__hierarchy__.append( (key, key.GetMother) )
	 			_subdir = Dir.Get(key.GetName())
	 			##-- And browsing inside recursively
				pytnp.counter += 1
	 			dictObjects = self.__extract__(_subdir,dictObjects)
	 			##-- To avoid segmentation faults, we need to return at the original directory
	 			##   in order to continue extracting subdirectories (or elements of the directory)
	 			_dirSave.cd()
	 		##-- Storing in the dictionary the interesting objects
	 		elif className == 'TCanvas' or className == 'RooFitResult' or className == 'RooDataSet' or \
	 				className == 'RooPlot':
			        #print Dir.GetPath().split(':/')[1]
				pytnp.counter += 1
				try:
					#Asuming unique id object-->complet path
					dictObjects[className][Dir.GetPath().split(':/')[1]+'/'+key.GetName()] = Dir.Get(key.GetName())
				except KeyError:
					dictObjects[className] = { Dir.GetPath().split(':/')[1]+'/'+key.GetName(): Dir.Get(key.GetName()) }
	 
	 	return dictObjects

	def ls(self,*arguments):
		"""
		FALLAAAAA
		"""
		directory = ''
		className = ''
		if len(arguments) > 2:
			print """
	You can not introduce more than 2 strings!
	                      """
			return
		elif len(arguments) == 1:
			directory = arguments[0]
			className = ''
		elif len(arguments) == 2:
			directory = arguments[0]
			className = arguments[1]


		isEnter = False
		for cl, pathDict in self.__dict__.iteritems():
			if cl.find(className) != -1:
				for path in pathDict.iterkeys():
					if path.find(directory) != -1:
						print path,' --> ',cl
						isEnter = True

		if not isEnter:
			print """
	'There\'s no matching with %s name'
	                      """ % directory

	def tableEff(self,name):
		"""
		"""
		try:
			dataSet = self.__dict__['RooDataSet'][name]
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




