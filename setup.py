from distutils.core import setup
setup(name='pytnp',
		version='0.4.1',
		description='Python for Tag And Probe utils',
		author='Jordi Duarte Campderros',
		author_email='Jordi.Duarte.Campderros@cern.ch',
		url='http://devel.ifca.es/~duarte/tnp/dist',
		#py_modules=['pytnpclass','__init__'],
		scripts=['effPlots.py','prepsubJobs.sh'],#'weightCreator.py],
		package_dir={'pytnp':''},
		packages=['pytnp','pytnp.utils'],
		)

