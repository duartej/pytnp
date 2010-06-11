#!/bin/sh
####                                            ####
### Script to send jobs to lxplus batch system.  ###
##  Needs the resonance name as argument and      ## 
#   the file fit_ResName.py is in the launching    #
##  directory.                                    ## 
###                                              ###
####J. Duarte Campderros, duarte@ifca.unican.es #### 

function parseOpt() 
{
	if [ $1 = "-o" ];
	then
		echo $1 $2
	fi

}

args=("$@")

if [ $# -lt 1 ]; then
        echo '================================================================='
	echo 'Error, I need the resonance name as argument:
                           JPsi|Upsilon'
        echo '================================================================='
        exit -1
fi

for i in `seq $#`;
do
	parseOpt ${arg[$i]} -->Averigua como se sustituia
done
exit


#RES=$1
#CATEGORIES='Glb POG_GlbPT TM POG_TMLSAT'

for CAT in $CATEGORIES;
do
	#EFF='MuonID TriggerFrom'
	for i in $EFF; 
	do
	
		if [ $i = 'MuonID' ]; 
		then
			PROCESS='TnP_MuFromTk'
	        elif [ $i = 'TriggerFrom' ];
	        then
			PROCESS='TnP_TriggerFrom'${CAT}
		fi
		CFG_OUT=fit_${RES}_${i}_${CAT}.py
		CFG_IN=fit_${RES}.py
		grep -B 100000 'process.TnP_MuFromTk = Template.clone(' $CFG_IN > $CFG_OUT
	        if [ $? -ne 0 ]; then
	        	echo '================================================================='
	 		echo 'Error, the file' $CFG_IN 'must exit here'
	        	echo '================================================================='
	                exit -1
	        fi
		cat >> $CFG_OUT<<EOF
    InputFileNames = cms.vstring(INPUTFILE),
    InputDirectoryName = cms.string("histoMuFromTk"),
    InputTreeName = cms.string("fitter_tree"),
    OutputFileName = cms.string(FILEPREFIX+"TnP_MuFromTk_${CAT}.root"),
    Efficiencies = cms.PSet(
        ${CAT}_pt_eta = cms.PSet(
            EfficiencyCategoryAndState = cms.vstring("${CAT}","pass"),
            UnbinnedVariables = cms.vstring("mass"),
            BinnedVariables = BINS,
            BinToPDFmap = cms.vstring("gaussPlusLinear")
        ),
    )
)
#----------- TRIGGER --------------
process.TnP_TriggerFrom${CAT} = Template.clone(
    InputFileNames = cms.vstring(INPUTFILE),
    InputDirectoryName = cms.string("histoTrigger"),
    InputTreeName = cms.string("fitter_tree"),
    OutputFileName = cms.string(FILEPREFIX+"TnP_TriggerFrom${CAT}.root"),
    Efficiencies = cms.PSet()
)

for trig in [ 'HLTMu3', 'L1DiMuOpen' ]:
    setattr( process.TnP_TriggerFrom${CAT}.Efficiencies, trig+'_pt_eta',
        cms.PSet(
            EfficiencyCategoryAndState = cms.vstring(trig,"pass"),
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
		OUTPUTDIR=/castor/cern.ch/user/d/duarte/BlindExercise/FIT02
        	cat > job_${RES}_${i}_${CAT}.sh<<EOF
#!/bin/sh

NOW=\$PWD
export VO_CMS_SW_DIR=/afs/cern.ch/project/gd/apps/cms
source \$VO_CMS_SW_DIR/cmsset_default.sh 
HOME_DIR=/afs/cern.ch/user/d/duarte
RELEASE_DIR=CMSSW/CMSSW_3_5_6/src

cd \$HOME_DIR/\$RELEASE_DIR
eval \`scramv1 runtime -sh\`

cd \$NOW
cmsRun $PWD/$CFG_OUT
OUTPUTFILE=\`ls *.root\`
rfdir $OUTPUTDIR
if [ \$? -ne 0 ]; then
rfmkdir $OUTPUTDIR
fi
rfcp \$OUTPUTFILE $OUTPUTDIR/\`echo \$OUTPUTFILE|awk -F. '{print \$1}'\`_${i}.root
EOF
	        chmod 755 job_${RES}_${i}_${CAT}.sh   
		
        	bsub -q 1nw -R 'pool>500' job_${RES}_${i}_${CAT}.sh
		done
done

