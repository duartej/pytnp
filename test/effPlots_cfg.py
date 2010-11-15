###########################################################################################
#DataNames: Dictionary to define the identifier and the latex (ROOT convention: \ -> #) 
#           description of a root file. 
#
#           Dictionary Keys: string with a pattern matching the name of the root file
#           Dictionary values: tuple of strings, the first item is the latex description
#                              and the second one the identifier for the root file.
DataNames = { 
		# root file name: TnP_Z_DATA_TriggerFromMu_Trigger_ProbeMu11_Eta_Fit.root
		'ProbeMu11_Eta_Fit': ( "Z#rightarrow#mu#mu, HLTMu11 trigger",'Z_11' ),		
		# root file is: TnP_Z_DATA_TriggerFromMu_Trigger_ProbeMu9_Eta_Fit.root
		'ProbeMu9_Eta_Fit' : ("Z#rightarrow#mu#mu, HLTMu9 trigger", 'Z_9' ),
	    }


###########################################################################################
#Attributes: Dictionaries to assign effType, objectType and isMC attributes to the pytnp
#            instances, the name of the dictionaries must be the ptynpname (identifier)
#            of the instance.
#
#            Dictionary Keys: string with the RooDataSet name
#            Dictionary values: tuple with effType (string), objectType(string) and isMC(int)

Z_11 = {
	  'tpTree/PASSING_all/fit_eff': ( 'HLT_trigger' , 'Glb_muons' , 0 ),
	  'tpTree/PASSING_all/cnt_eff': ( 'HLT_trigger' , 'Glb_muons' , 1 ),
       }

Z_9 = {
	  'tpTree/PASSING_all/fit_eff': ( 'HLT_trigger' , 'Glb_muons' , 0 ),
	  'tpTree/PASSING_all/cnt_eff': ( 'HLT_trigger' , 'Glb_muons' , 1 ),
       }

