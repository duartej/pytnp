#!/usr/bin/env python

#import ROOT
#import FWCore.ParameterSet.Config as cms
#ROOT.gROOT.SetBatch(1)

import sys
if sys.version_info < (2,6):
	message = '\033[1:31mError: I need python 2.6 or greater. Also I need the CMSSW_3_5_6 or greater environment set\033[1;m'
	print message
	exit(-1)

def findTrees( Dir, treeList ):
	"""
	findTrees( ROOT.TFile ) -> [ 'nameOftheTree1', ... ]

	Getting a T&P Ntuple, get the name of all the trees
	"""
 	_dirSave = Dir
	#Storing the father->child info
	try:
		listOfKeys = Dir.GetListOfKeys()
	##-- Checking that is a Tag and Probe fit 
	##   file. IF it is not, then we find
	##   some not expected TKeys diferent from TTree
	except AttributeError:
		message = """\033[1;31mError: The root file is not an standard T&P NTuple file\033[1;m""" 
		raise AttributeError, message
 	for key in Dir.GetListOfKeys():
 		className = key.GetClassName()
 		if key.IsFolder() and className != 'TTree': #Watch TTree is a folder
 			##-- Extracting the Folder from Dir
			_subdir = Dir.Get(key.GetName())
 			##-- And browsing inside recursively
 			treeList = findTrees(_subdir,treeList)
 			##-- To avoid segmentation faults, we need to return
			##   at the original directory in order to continue
			##   extracting subdirectories (or elements of the directory)
 			_dirSave.cd()
 		##-- Storing in the dictionary the interesting objects
 		elif className == 'TTree':
			#Asuming unique id object-->complet path
			treeList.append( Dir.GetPath().split(':/')[1]+'/'+key.GetName() )
 
 	return treeList

def searchEndBlock( strList ):
	"""
	searchEndBlock( 'strList' ) -> 'newstr'

	Function to extract from a string, the contents
	between two more external parenthesis
	"""
	index0 = strList.find('(')+1
	numP = 1
	for c in xrange(index0,len(strList)):
		if strList[c] == ')':
			numP -= 1
		elif strList[c] == '(':
			numP += 1
		
		if numP == 0:
			return strList[:c+1]


def findCategory( _file, _treeName ):
	"""
	findCategory( ROOT.TFile ) -> [ category1, category2, ... ]
	
	Return alist with the names for the muon categories found in
	a NTuple T&P root file. If there are multiple categories, 
	as a trigger path for a muon category, then the list contains
	'Muoncategory:triggerPath' such elements.
	"""
	tree = _file.Get(_treeName)
	#Name of the EDAnalyzer
	edmAnName = _treeName.split('/')[0]
	#Get MetaData 
	metadata = tree.GetUserInfo()[0].GetString().Data()
	# Isolating the EDAnalyzer with its parameters
	parameters = metadata[metadata.find(edmAnName+':'):]
	parameters = searchEndBlock( parameters )
	# Getting the categories
	catStr = parameters[parameters.find('flags:'):]
	catStr = searchEndBlock( catStr )
	categories = []
	triggerCat = []
	for i in catStr.split('\n'):
		# Pairing Triggers with the rest of categories 
		if i.find('triggerObjectMatches') != -1:
			triggerCat.append( i.split(':')[0].strip(' ') ) 
		elif i.find('string tracked') != -1 or i.find('InputTag tracked') != -1:
			categories.append( i.split(':')[0].strip(' ') )
	#Add the trigger to build categories with to checks
	deliverCat = None
	if len(triggerCat) == 0:
		deliverCat = categories
	else:
		deliverCat = []
		for trigger in triggerCat:
			for cat in categories:
				deliverCat.append( cat+':'+trigger )
	return deliverCat	


#TODO: Por el momento, el trigger me sigue jodiendo... no es trivial 
def writeConfig( _file, _dirName, weightList ):
	"""
	"""
	import shutil
	# Backup copy
	copyFile = _file.replace('.py','_bck.py')
	try:
		shutil.copy( _file, copyFile )
	except IOError:
		message = '\033[1;31mError: There is no config File named %s\033[1;m' % configPy
		raise IOError, message
	message = """\033[1;34m Saved a copy, including the weights, for your fit phyton config file %s, named as %s\033[1;m """ % ( _file, copyFile )
	print message
	#Reading the file
	_configPy = open(copyFile)
	_lines = _configPy.readlines()
	numIndex = filter( lambda i: i.find('process.'+_dirName) != -1 , _lines )
	if len(numIndex) == 0:
		message = '\033[1;31mError: There is no process called %s in the %s config file named\033[1;m' % ( _dirName, configPy )
		raise IOError, message
	numIndex = numIndex[0]

	#################################### TODO #####################




def extractBINS( configPy, var ):
	"""
	"""
	import shutil
	import os
	#TODO: Better a temporary file
	try:
		shutil.copy( configPy, '_tmpPy.py')
	except IOError:
		message = '\033[1;31mError: There is no config File named %s\033[1;m' % configPy
		raise IOError, message
	# To be sure the first import is FWCore.ParameterSet.Config 
	# in order to extract BINS
	_file = open('_tmpPy.py','r')
	_lines = _file.readlines()
	_file.close()
	_lines.insert(0,'import FWCore.ParameterSet.Config as cms\n')
	_file = open('_tmpPy.py','w')
	_file.writelines(_lines)
	_file.close()
	#------------------------------------------------------------     
	
	try:
		from _tmpPy import BINS
	except ImportError:
		message = '\033[1;31mError: There is no BINS in %s file. Are you sure this is a config python to do the fit?\033[1;m' % configPy
		os.remove('_tmpPy.py')
		raise ImportError, message

	variables = BINS.parameterNames_()
	# Check if the variables introduced by the user are inside
	# the fit config python
	for i in var:
		if i not in variables:
			os.remove('_tmpPy.py')
			message = """\033[1;31mError: The variable %s is not in the parameter BINS of the config python %s. 
Check your config or change your input variable with --var option\033[1;m """ % ( i, configPy)
		        print message
                        raise KeyError

	# All was fine. Remember: first variable is the pt-like (construct the weights respect it)
	PT = variables[0]
	ETA = variables[1]

	#bins = BINS
	try:
		os.remove( '_tmpPy.py' )
		os.remove( '_tmpPy.pyc' )
	except OSError:
		pass

	return BINS,PT,ETA


def makeWeights(_files,treeName,category,_outputFile, BINS, PT, ETA):
	"""
	makeWeights( _fileDict, 'treename', 'category', 'outputfile' ) -> 
	"""
	import ROOT
	ROOT.gROOT.SetBatch(1)

	#treeName = 'histoMuFromTk/fitter_tree'
	_trees = dict( [ ( name, _file.Get(treeName) ) for name,_file in _files.iteritems()] )
	#Check if in both files are the tree
	for _tree in _trees.itervalues():
		if not _tree:
			return None
	
	histos = {}
	weights = {}

	#checking if category contains a trigger also
	condCategory = category+' == 1'
	if category.find(':') != -1:
		_catList = category.split(':')
		muonCat = _catList[0]
		triggerCat = _catList[1]
		condCategory = muonCat+' == 1 && '+triggerCat+' == 1'

	instName = lambda k,pt : PT+'>>h_'+category+name+str(k)+'(50,'+str(pt[0])+','+str(pt[1])+')'
	cuts = lambda pt,eta: PT+' >= '+str(pt[0])+' && '+PT+' <'+str(pt[1])+\
			' && '+ETA+' >= '+str(eta[0])+' && '+ETA+' < '+str(eta[1])+' && '+condCategory
	k = 0
	for i in xrange(len(BINS.__getattribute__(PT))-1):
		pt = (BINS.__getattribute__(PT)[i],BINS.__getattribute__(PT)[i+1])
		for j in xrange(len(BINS.__getattribute__(ETA))-1):
			eta = (BINS.__getattribute__(ETA)[j],BINS.__getattribute__(ETA)[j+1])
			for name,_t in _trees.iteritems(): 
				N = _t.Draw( instName(k,pt),cuts(pt,eta) )
				histos[name] = ROOT.gDirectory.Get('h_'+category+name+str(k))
			print '  \033[1;34mDoing bin'+str(k)+' '+PT+'=('+str(pt[0])+','+str(pt[1])+') '+ETA+'=('+str(eta[0])+','+str(eta[1])+')\033[1;m'
			swap =  histos['numerator'].Clone(category+'_bin'+str(k))
			dummy = swap.Divide(histos['denominator'])
			weights[category+'_bin'+str(k)] =( (eta[0],eta[1]), (pt[0],pt[1]), ROOT.gDirectory.Get(category+'_bin'+str(k)) )
			#Acura els limits
			weights[category+'_bin'+str(k)][2].GetXaxis().SetLimits( pt[0], pt[1] )  
			weights[category+'_bin'+str(k)][2].SetNormFactor(1)  
			k += 1
	_out = ROOT.TFile(_outputFile,'RECREATE')
	for name,(etaBins,ptBins,histo) in weights.iteritems():
		histo.Write()
	_out.Close()	
	return weights


def getWeightsFromFile(fileW,category,BINS,PT,ETA):
	"""
	getWeightsFromFile( ROOT.TFile, 'category', FWCore.ParameterSet.Config.BINS, 'PT', 'ETA' ) ->
	"""
	mapBinVal = {}
	weights = {}
	k = 0
	for i in xrange(len(BINS.__getattribute__(PT))-1):
		pt = (BINS.__getattribute__(PT)[i],BINS.__getattribute__(PT)[i+1])
		for j in xrange(len(BINS.__getattribute__(ETA))-1):
			eta = (BINS.__getattribute__(ETA)[j],BINS.__getattribute__(ETA)[j+1])
			weights[category+'_bin'+str(k)] = ( eta, pt, fileW.Get(category+'_bin'+str(k)) )
			try:
				weights[category+'_bin'+str(k)][2].GetXaxis().SetLimits( pt[0], pt[1] )  
			except AttributeError:
				# Then we are using a binning different of this one which contains the weight_out file
				message = """\033[1;31mError: The binning defined by the config python file is different than
the defined in the weights_out_*.root files. If your config file is correct,
un this script in another location (to avoid remove the weights_out_*.root 
files). These are the bins used by the config python you have introduced 
%s\033[1;m""" % str(BINS)
				print message
				raise AttributeError
			k += 1

	return weights


def redoTuple( fileRootName, treeName, categoryList, weightsDict, PT, ETA ):
	"""
	redoTuple( 'filename', 'treename', ['cat1',...] , {} ) ->
	"""
	import ROOT
	import sys
	# Dictionary to store the names of the branches
	valueName = {}
	# Dictionary to store the struct C++ objects pythonized
	theW = {}
	for category in categoryList:
		name = 'weight_'+category.replace(':','_')
		valueName[category] = name
		code = 'struct W_'+category.replace(':','_')+'{ double '+name+'; };'
		structName = 'W_'+category.replace(':','_')
		# Creation of the C++ struct in ROOT
		ROOT.gROOT.ProcessLine( code )
		# Importing the C++ struct and initializing
		_tmp  = __import__('ROOT',fromlist=[structName])
		_toInit = _tmp.__getattr__( structName )
		theW[category] = eval( '_toInit()' )

	counter = 0
	count2Print = '\033[1;34mRe-doing NTuple %s for tree %s: %s%s\033[1;m' % ( fileRootName, treeName.split('/')[0], str(int(counter)).zfill(2),'%' )
	sys.stdout.write( count2Print )

	fileRoot = ROOT.TFile( fileRootName,'UPDATE' )
	# FIXME: Check if is in there the root file
	t = fileRoot.Get( treeName )
	# Get all the branches: to extract the variables 
	var = dict( [ (i.GetName(),t.GetLeaf(i.GetName())) for i in t.GetListOfBranches() ] )

	count = 0
	lastCounter = 0
	theBranches = {}
	for category,_branchName in valueName.iteritems():
		theBranches[ _branchName  ] = t.Branch( _branchName, theW[category], _branchName+'/D' )
	numEntries = t.GetEntries()
	for i in xrange(numEntries):
		dumm = t.GetEntry(i)
		pt = var[PT].GetValue()
		eta = var[ETA].GetValue()
		for category, weights in weightsDict.iteritems():
			for name,(etaBins, ptBins, histo) in weights.iteritems():
				if eta >= etaBins[0] and eta < etaBins[1] and pt >= ptBins[0] and pt < ptBins[1]:	
					bin = histo.FindBin( pt )
					theW[category].__setattr__( valueName[category], histo.GetBinContent(bin) )
					break
		counter	= int(float(count)/numEntries*100)
		if counter % 10 != lastCounter:
			sys.stdout.write( '\033[1;33m \b\b\b\b'+str(counter).zfill(2)+'%\033[1;m' )
			sys.stdout.flush()
			lastCounter = counter % 10
		for theBranch in theBranches.itervalues():
			dumm = theBranch.Fill()
		count += 1 
	sys.stdout.write( '\033[1;33m \b\b\b\b'+str(100).zfill(2)+'%\n\033[1;m' )
	sys.stdout.flush()
	
	_dir = fileRoot.Get(treeName.split('/')[0])
	_dir.cd()
	t.Write('',ROOT.TObject.kOverwrite)
	fileRoot.Close()

def main(opt):
	"""
	"""
	import shutil
	import ROOT
	# weights = { 'bin#': ( (eta_min,eta_max), ROOT.TH1F ) ,
	#             .... }
	# Checking th config file and extracting info from there

	BINS, PT, ETA = extractBINS( opt.configPy, opt.var )

	_files = {}
	#FIXME: Controlar un unico fichero de entrada -i 
	numeratorFileName = opt.numName #FIXME

	#Files as numerator of the weights
	_files[ 'numerator' ] = ROOT.TFile(numeratorFileName)
	#File as denominator of the weights
	_files[ 'denominator' ] = ROOT.TFile(opt.denName)
	#Checking the files exist:
	for _nameFile, _rootFile in _files.iteritems(): 
		if _rootFile.IsZombie():
			message = """\033[1;31mError: the file name %s introduced is not exist\033[1;m""" % _nameFile
			raise IOError,message
	
	#Copying denominator file to put the weights in there
	headStr = opt.denName.split('/')[-1].split('_')[0]
	tailStr = ''
	for i in opt.denName.split('/')[-1].split('_')[1:]:
		tailStr += '_'+i
	_wOutputName = headStr+'_ReWeighted'+tailStr
	print '\033[1;34mCopying from %s the new file which will store weights: %s\033[1;m' % (opt.denName,_wOutputName)
	shutil.copy( opt.denName, _wOutputName ) 
	#FIXME: Check if is ok

	#Find how many trees we have
	treesInNumerator = set( findTrees( _files['numerator'], [] ) )
	treesInDenominator = set( findTrees( _files['denominator'], [] ) )
	treesInCommon = treesInNumerator.intersection( treesInDenominator )
	#Using only those trees common to both files
	trees = list( treesInCommon )
	treeCatDict = dict( [ (name, None) for name in trees ] )

	#Find what categories we have; for each tree we have a list of
	#Muon categories
	for _tree in treeCatDict.iterkeys():
		#Extracting the ROOT.TTree
		#To avoid the histograms get lost over the memory
		_fileW = {}
		weightsDict = {}
		treeCatDict[_tree] = findCategory( _files['denominator'], _tree )
		for cat in treeCatDict[_tree]:
			_fileWName = 'weights_out_'+_tree.split('/')[0]+'_'+cat.replace(':','_')+'.root'
			_fileW[ _fileWName ] = ROOT.TFile(_fileWName)
			#If we have done previosly the weights, don't do it again
			if _fileW[_fileWName].IsZombie():
				_fileW[_fileWName].Delete()
				del _fileW[ _fileWName ]
				print '\033[1;34mCreating the TH2F weights root files. Ignore the \'Error in <TFile::TFile>\' messages\033[1:m' 
				weights = makeWeights(_files,_tree,cat,_fileWName,BINS,PT,ETA)
			else:
				weights = getWeightsFromFile(_fileW[_fileWName],cat,BINS,PT,ETA)
			weightsDict[ cat ] = weights
		#if _tree == 'histoTrigger/fitter_tree': #----> DEBUG!!!
		#	continue
		# Rebuild the Ntuple including the weights	
		redoTuple( _wOutputName, _tree, treeCatDict[_tree], weightsDict, PT, ETA )
	message = '\033[1;34mUpdated %s with the weights for' % _wOutputName
	for i in treeCatDict.iterkeys():       
		message += ' '+i+','
	message = message[:-1]+' directories\033[1;m'
	_c = len(message)
	print '='*_c
	print message
	print '='*_c
	# Recall to include the weights in the config python file (see writeConfig function --> TODO)
	message = """\033[1;33mRemember to include the weights in the config file %s\n""" % opt.configPy
	for _dir, categoryList in treeCatDict.iteritems():
		message += """\033[1;34m   Include this line inside efficiency PSet of the categories in tree: %s\n """ % _dir
		for _cat in categoryList:
			message += """\033[1;34m      - %s --> weight = cms.string("%s") \n """ % ( _cat, 'weight_'+_cat.replace(':','_') )
	message += """\033[1;m"""
	print message		




if __name__ == '__main__':
	"""
	"""
	#import shutil
        from optparse import OptionParser
	#from pytnp.utils.getresname import getResName 

        parser = OptionParser()
	parser.set_defaults(counting=False)
        parser.add_option( '-d', '--denominator', nargs = 1, action='store', dest='denName', metavar='FILENAME', help='Input root file name to use as denominator ( J/Psi usually)' )
        parser.add_option( '-n', '--numerator', nargs = 1, action='store', dest='numName', help='Input root file name to use as numerator' )
        parser.add_option( '-p', '--configPy', nargs = 1, action='store', dest='configPy', help='Configuration python to be used in the fit process' )
        parser.add_option( '--var', nargs = 2, action='store', type = 'string', dest='var', help='Binned variables names. The first one is used to construct the weights respect to it. ' )
        parser.add_option( '-c', '--category', action='store', dest='category', help='Muon category to build the weights (coma separeted list, no espace)' )

        ( opt, args ) = parser.parse_args()

	if not opt.numName:
		Message="""Missed mandatory argument -n FILENAME"""
		parser.error( Message )
	if not opt.denName:
		Message="""Missed mandatory argument -d FILENAME"""
		parser.error( Message )
	if not opt.configPy:
		Message="""Missed mandatory argument -p CONFIGFILE"""
		parser.error( Message )
	if not opt.var:
		Message="""Missed mandatory argument --var Var1 Var2"""
		parser.error( Message )

	main( opt )


