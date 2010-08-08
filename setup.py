from distutils.core import setup, Extension
from subprocess import Popen, PIPE


# Generating the c++ executables  ---------------------
# FIXME: Provisional code--> missing checks, error
#        control, ...
import os
import shutil
print '\033[1;39mGenerating C++ executables...\033[1;m'
oldPath = os.getcwd()
os.chdir('procsfile')
_sources = filter( lambda x: os.path.isfile(x), os.listdir('.') )
try:
	os.mkdir('.build')
	for _file in _sources:
		shutil.copy(_file,'./.build/'+_file)
except OSError:
	pass
os.chdir('.build')
ccode = Popen( ['make'],stdout=PIPE).communicate()[0]
print ccode
os.chdir( oldPath )
#-------------------------------------------------------


setup(name='pytnp',
		version='0.6.0',
		description='Python for Tag And Probe utils',
		author='Jordi Duarte Campderros',
		author_email='Jordi.Duarte.Campderros@cern.ch',
		url='http://devel.ifca.es/~duarte/tnp/dist',
		#py_modules=['pytnpclass','__init__'],
		scripts=['effPlots.py','prepsubJobs.sh','weightCreator.py', 'procsfile/.build/copyFile', 'procsfile/.build/CowboysNTuple'],
		package_dir={'pytnp':''},
		packages=['pytnp','pytnp.utils'],
		)

