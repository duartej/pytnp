#!/usr/bin/env python
"""
skimEfficiency: check the efficiency of the skimming for the differents paths
"""

def sumEff( stdoutFile, sumDict ):
	"""
	"""
	import re

	if type(sumDict) is not dict:
		errorMessage = """
findBlock( stdoutFile, sumDict ) --> second argument must be a dict, but is %s""" % repr(type(a))

	f = open( stdoutFile )
	lines = f.readlines()
	counter = 0
	counterDOWN = 0
	for l in lines:
		if l.find( 'TrigReport ---------- Path   Summary ------------' ) != -1:
			counterDOWN = counter
		if l.find( 'TrigReport -------End-Path   Summary ------------' ) != -1:
			break
		counter += 1

	regexp = re.compile( '\D*\s*\S\s*\S\s*(?P<RUN>\d*)\s*(?P<Passed>\d*)\s*(?P<Failed>\d*)\s*\d\s*(?P<NAME>.*)$' )
	for i in xrange(counterDOWN+2,counter-1):
		name = regexp.search( lines[i] ).group( 'NAME' )
		try:
			sumDict[name]['RUN'] += int(regexp.search( lines[i] ).group( 'RUN' )) 
			sumDict[name]['Passed'] +=  int(regexp.search( lines[i] ).group( 'Passed' ))
			sumDict[name]['Failed'] += int(regexp.search( lines[i] ).group( 'Failed' ))
		except KeyError:
			sumDict[name] = {}
			sumDict[name]['RUN'] = int(regexp.search( lines[i] ).group( 'RUN' )) 
			sumDict[name]['Passed'] = int(regexp.search( lines[i] ).group( 'Passed' )) 
			sumDict[name]['Failed'] = int(regexp.search( lines[i] ).group( 'Failed' ))

	return sumDict


def showResults( sumDict, format='' ):
	"""
	"""
	# FIXME: Sort filters in a logical order 
	if format == 'latex':
		#TODO
		pass
	toShow = '%s %s %s %s %s\n' % (''.ljust(20),'Runned'.rjust(10),'Passed'.rjust(10),'Failed'.rjust(10),'eff'.rjust(10) )
	toShow += '\n'
	for filter,status in sumDict.iteritems():
		toShow += """%s %10d %10d %10d %10f\n""" \
				% (filter.ljust(20),status['RUN'],status['Passed'],status['Failed'],status['Passed']/float(status['RUN']))
	print toShow
		

if __name__ == '__main__':
	from optparse import OptionParser
	
	parser = OptionParser()
#fname = 'trackerRecoMaterial_3_2_7.xml'
	parser.set_defaults(incdir = '.')
        parser.add_option( '-d', '--dir', action='store', dest='incdir', help='Directory (absolute or relative) where are the files' )

        ( opt, args ) = parser.parse_args()
	import os
	allFiles = filter( lambda x: ( x.find('CMSSW_') != -1 and x.find('.stdout') != -1 ), os.listdir(opt.incdir) )
	if len(allFiles) == 0:
		errorMessage =  'Directory %s doesn\'t contains the CMSSW_*.stdout, insert a directory with \'-d\' option' % opt.incdir
		parser.error( errorMessage )

	print '='*50
	print 'Reporting skimming efficiencies, processed datasets: ', len(allFiles)

	effTable = {}
	for stdoutFile in allFiles:
		effTable = sumEff( os.path.join(opt.incdir,stdoutFile), effTable )

	showResults( effTable )
		
		
	
	


