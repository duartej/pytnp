#!/bin/sh
####################################################
####                                            ####
### Script to send jobs to lxplus or gridui      ###
##  (IFCA SITE) batch system.                     ##
#   Needs the resonance name as argument and       # 
#   the file fit_ResName.py is in the launching    #
##  directory.                                    ## 
###                                              ###
####J. Duarte Campderros, duarte@ifca.unican.es #### 
####################################################

# Function to show script usage
usage()
{
cat << EOF
usage: $0 [options] PYNAME

Build the configuration python files based in fit_PYNAME.py
for each CATEGORY (passed with -c mandatory option) and the
.sh jobs which will be send to the lxplus or gridui batch system. 

OPTIONS:
   -h                   Show this message
   -c "CAT1 CAT2 ..."   Categories (Glb, TMLSAT, ...) in a list space
                        separated and bounded by " ". The name must 
 	                be the same as it is found in the TnP trees 
                        (Ntuples).   
   -e "MuonID Trigger"  Efficiencies types in a list space separated
                        and bounded by " ". Valid names are:
                             MuonID
		             Trigger	     
   -o OUTPUTDIR         (castor) output directory (mandatory)
   -r RELEASEDIR        complete path for the CMSSW release directory 
   -w                   include the weights
   -s	                simulate, create the files but without sending
                        to batch system 
EOF
}

SIMULATE=false
#Getting options
while getopts "h:c:e:o:r:sw" OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         c)
             CATEGORIES=$OPTARG
	     #Check errors
             ;;
	 e)
	     EFF=$OPTARG
	     #Check if arguments are right
	     ;;  
	 o)  
             OUTPUTDIR=$OPTARG
             ;;
         r)
	     RELEASE_DIR=$OPTARG
	     #Check if dir exists
             ;;	     
         s)
	     SIMULATE=true
             ;;	     
         w)
	     WEIGHT="cms.string(\"weight"
             ;;	     
         ?)
             usage
             exit
             ;;
     esac
done
#Recover the #of arguments without - options
shift $(($OPTIND - 1))

##########################################################################################
# Checkin arguments
##########################################################################################
if [ -z "$CATEGORIES" ]; then
	CATEGORIES='Glb POG_GlbPT TM POG_TMLSAT'
	echo 
	echo 'WARNING: I am using this categories ' $CATEGORIES
	echo 'Uses the -c option if you want to specified them'
	echo
fi
if [ -z "$EFF" ]; then
	EFF="MuonID Trigger"
	echo 
	echo 'WARNING: I am using this efficiencies ' $EFF
	echo 'Uses the -e option if you want to specified them'
	echo
fi
if [ -z "$OUTPUTDIR" ]; then
        echo '==================================================================='
	echo 'Error, I need the name for the castor output file  '
        echo '==================================================================='
	usage
	exit -1
fi
if [ -z "$RELEASE_DIR" ]; then
        echo '==================================================================='
	echo 'Error, I need the name of the CMSSW release dir'
        echo '==================================================================='
	usage
	exit -1
else
   	if [ ! -d $RELEASE_DIR ]; then
		echo '==================================================================='
		echo 'Error, the directory' $RELEASE_DIR ' not exist'
		echo '==================================================================='
		exit -1
   	fi
fi
if [ $# -lt 1 ]; then
        echo '==================================================================='
	echo 'Error, I need the name from the configuration python file you are  '
        echo 'going to use.'                           
        echo '==================================================================='
        usage
        exit -1
else
	RES=$1
fi

CFG_IN=fit_${RES}.py
if [ ! -f $CFG_IN ]; then
        echo '==================================================================='
	echo 'Error, the file ' fit_${RES}.py 'must exist here'                  
        echo '==================================================================='
	exit -1
fi
##########################################################################################


##########################################################################################
#  Getting the BATCHSYSTEM and the copy commands associated
##########################################################################################
BATCHSYSTEM=`hostname |awk -F. '{ print $1 }'|sed s/[0-9]//g`
if [ "X$BATCHSYSTEM" = "Xgridui" ]; 
then
	CP=cp
	MKDIR=mkdir
	LS=ls
	SUBMITER="qsub -P l.gaes -cwd -l h_rt=180:0:0 "  #---> Changes here tha CPU time
elif [ "XBATCHSYSTEM" = "Xlxplus" ]; 
then
	CP=rfcp
	MKDIR=rfmkdir
	LS=rfdir
	SUBMITER="bsub -q 1nw -R 'pool>500' "        #---> Changes here the spool (1nw, 8nh, ..)
else
        echo '==================================================================='
	echo 'Error, Unrecognized batch system: "$BATCHSYSTEM"                   '
	echo '       Sopported batch system are: gridui, lxplus                  '
        echo '==================================================================='
	exit -1
fi
##########################################################################################

#RES=$1

for CAT in $CATEGORIES;
do
	#EFF='MuonID TriggerFrom'
	for i in $EFF; 
	do
	
		#Including the weights
		if [ $WEIGHT ]; 
		then
			WEIGHT_MUONID="weight = "${WEIGHT}_$CAT\""),"
			WEIGHT_TRIGGER="weight = eval('"${WEIGHT}_${CAT}_"'+trig+'\")'),"

		fi
		CFG_OUT=fit_${RES}_${i}_${CAT}.py
		if [ $i = 'MuonID' ]; #---------------------  MUONID UF
		then
			PROCESS='TnP_MuFromTk'
			grep -B 100000 'process.TnP_MuFromTk = Template.clone(' $CFG_IN > $CFG_OUT
			cat >> $CFG_OUT<<EOF
    InputFileNames = cms.vstring(INPUTFILE),
    InputDirectoryName = cms.string("histoMuFromTk"),
    InputTreeName = cms.string("fitter_tree"),
    OutputFileName = cms.string(FILEPREFIX+"TnP_MuFromTk_${CAT}.root"),
    Efficiencies = cms.PSet(
        ${CAT}_pt_eta = cms.PSet(
            EfficiencyCategoryAndState = cms.vstring("${CAT}","pass"),
	    $WEIGHT_MUONID
            UnbinnedVariables = cms.vstring("mass"),
            BinnedVariables = BINS,
            BinToPDFmap = cms.vstring("gaussPlusLinear")
        ),
    )
)

process.p = cms.Path(
	process.$PROCESS
        )
        
EOF
	        elif [ $i = 'Trigger' ]; #--------------------- TRIGGER IF
	        then
			PROCESS='TnP_TriggerFrom'${CAT}
			grep -B 100000 'process.TnP_TriggerFrom'${CAT}' = Template.clone(' $CFG_IN > $CFG_OUT
			cat >> $CFG_OUT<<EOF
    InputFileNames = cms.vstring(INPUTFILE),
    InputDirectoryName = cms.string("histoTrigger"),
    InputTreeName = cms.string("fitter_tree"),
    OutputFileName = cms.string(FILEPREFIX+"TnP_TriggerFrom_${CAT}.root"),
    Efficiencies = cms.PSet()
)

for trig in [ 'Mu3', 'L1DoubleMuOpen' ]:
    setattr( process.TnP_TriggerFrom${CAT}.Efficiencies, trig+'_pt_eta',
        cms.PSet(
            EfficiencyCategoryAndState = cms.vstring(trig,"pass"),
	    $WEIGHT_TRIGGER
            UnbinnedVariables = cms.vstring("mass"),
            BinnedVariables = BINS.clone(
                ${CAT} = cms.vstring("pass")
            ),
            BinToPDFmap = cms.vstring("gaussPlusLinear")
        )
    )

process.p = cms.Path(
	process.$PROCESS
        )
        
EOF
		fi                       # ----------------- END IF MUON-TRIGGER
 
		cat > job_${RES}_${i}_${CAT}.sh<<EOF
#$ -S /bin/sh

NOW=\$PWD
#export VO_CMS_SW_DIR=/afs/cern.ch/project/gd/apps/cms --> Must exist an VO_CMS_SW_DIR, check it
source \$VO_CMS_SW_DIR/cmsset_default.sh 

cd $RELEASE_DIR
eval \`scramv1 runtime -sh\`

cd \$NOW
cmsRun $PWD/$CFG_OUT
OUTPUTFILE=\`ls *.root\`
$LS $OUTPUTDIR
if [ \$? -ne 0 ]; then
$MKDIR $OUTPUTDIR
fi
$CP \$OUTPUTFILE $OUTPUTDIR/\$OUTPUTFILE
EOF
	        chmod 755 job_${RES}_${i}_${CAT}.sh   
		if $SIMULATE; then
		       echo '***********************************************************'
		       echo 'Not sended to batch system'
		       echo 'If you want to send, use this command:'
		       echo ' '$SUBMITER' job_'${RES}'_'${i}'_'${CAT}'.sh'
		       echo '***********************************************************'
	        else
		       eval $SUBMITER job_${RES}_${i}_${CAT}.sh
	        fi     
		done
done

