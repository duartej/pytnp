/*
   CowboysNTuple.cpp

   copies the contents of a File, but only
   storing the good events (it is good Cowboys
   and Seagulls).

Compilation: gcc `root-config --libs` -I`root-config --incdir` -o CowboysNTuple CowboysNTuple.cpp

Arguments: * Name of the input dataset
           -o Name of the output dataset


   J. Duarte Campderros, C. Jorda, 01-06-2010
   (based of an example from http://cern.ch/root/tutorials..) 

   duarte@ifca.unican.es
   cjorda@ifca.unican.es
*/
#ifndef __CINT__

#include<string>
#include<iostream>
#include<stdio.h>
#include<stdlib.h>
#include<cmath>

#include "TDirectory.h"
#include "TROOT.h"
#endif

#include "TKey.h"
#include "TFile.h"
#include "TSystem.h"
#include "TTree.h"
#include <exception>

bool putGoodEvents(TTree *oldT, TTree *newT)
{
	std::cout << "/" << oldT->GetName() << " Total number of events: ";
	Float_t pair_dphiVtxTimesQ = 0.0;
	Float_t tag_eta = 0.0;
	Float_t eta = 0.0;
	int goodEvents = 0;
	
	//WARNING: Hardcoded branches
	oldT->SetBranchAddress("pair_dphiVtxTimesQ",&pair_dphiVtxTimesQ);
	oldT->SetBranchAddress("tag_eta",&tag_eta);
	oldT->SetBranchAddress("eta",&eta);
	
	int nEntries = oldT->GetEntries();
	std::cout << nEntries; 
      	for(int event=0; event < nEntries; ++event)
	{
		oldT->GetEntry(event);

		bool seagulls = pair_dphiVtxTimesQ < 0.0 ;
		bool goodCowboys = ( pair_dphiVtxTimesQ > 0.0 && fabs(tag_eta-eta)>0.2 );
		if(  seagulls || goodCowboys) 
		{
			++goodEvents;
		  	newT->Fill();
	    	}
      	}

	if (goodEvents == 0)
	{
		std::cout << std::endl;
		std::cout << "--------> WARNING: Skipping Tree, missed branch. Ignore the above Error message <--------" << std::endl;
		return false;
	}
	std::cout << ", number of good events: " << goodEvents << std::endl;
	return true;
}


void CopyDir(TDirectory *source) {
      	//copy all objects and subdirs of directory source as a subdir of the current directory   
      	//source->ls();
      	TDirectory *savdir = gDirectory;
	TDirectory *adir = 0;
      	if(source->InheritsFrom(TFile::Class()))
      	{
		adir = gDirectory;
      	}
      	else
      	{ 
		adir = savdir->mkdir(source->GetName());
      	}
      	adir->cd();
      	//loop on all entries of this directory
      	TKey *key;
      	TIter nextkey(source->GetListOfKeys());
      	while ((key = (TKey*)nextkey())) 
	{
		const char *classname = key->GetClassName();
		TClass *cl = gROOT->GetClass(classname);
		if (!cl)
		{
			continue;
		}

		if (cl->InheritsFrom(TDirectory::Class())) 
		{
		  	source->cd(key->GetName());
		  	TDirectory *subdir = gDirectory;
		  	adir->cd();
		  	CopyDir(subdir);
		  	adir->cd();
	    	} 
		else if (cl->InheritsFrom(TTree::Class())) 
		{
			TTree *T = (TTree*)source->Get(key->GetName());
		  	adir->cd();
			std::cout << "Filling the directory " << adir->GetName(); 
			//Empty copy of the tree
		  	TTree *newT = T->CloneTree(0);
			//Filling the good cowboys and seagulls events only
			if ( putGoodEvents(T,newT) )
			{
				newT->Write();
			}
	    	} 
		else 
		{      
			source->cd();
		  	TObject *obj = key->ReadObj();
		  	adir->cd();
		  	obj->Write();
		  	delete obj;
	    	}
      	}
      	adir->SaveSelf(kTRUE);
      	savdir->cd();
}

void CopyFile(const char *inputName, const char *outputName, int NumEntries=-1) 
{
      	TFile *foutput = new TFile(outputName,"recreate");
      	//Copy all objects and subdirs of file fname as a subdir of the current directory
      	TDirectory *target = gDirectory;
      	TFile *finput = TFile::Open(inputName);
      	if (!finput || finput->IsZombie()) 
	{
	    	printf("Cannot copy file: %s\n",inputName);
	    	target->cd();
	    	return;
      	}
      	target->cd();
      	CopyDir(finput);
      	delete finput;
      	target->cd();
      	delete foutput;
}


#ifndef __CINT__
int main( int argc, const char* argv[] )
{
	int Nentries;
	bool isN = false;
	std::string _output;
	bool isOutputFile = false;
	std::string _input;
	
	//Parsing input options
	if(argc == 1)
	{
		std::cout << "usage: copyFiles inputFileName.root [options]" << std::endl;
		std::cout << "" << std::endl;
		std::cout << "Options:" << std::endl;
		std::cout << "    -o nameOutputFile.root " << std::endl;
		std::cout << "" << std::endl;
		return -1;
	}
	else if( argc == 2)
	{
		_input = argv[1];
		Nentries = -1; //All entries
		_output = "outputFile.root";
	}
	else
	{
		//Argumet 1 must be a valid input fileName
		_input = argv[1];
		for (int i = 2; i < argc; i++) 
		{
			if( strcmp(argv[i],"-o") == 0 )
			{
				_output = argv[i+1];
				isOutputFile = true;
			}
		}
		//Check the values
		if( ! isN )
		{
			Nentries = -1;
		}
		if( ! isOutputFile )
		{
			_output = "outputFile.root";
		}
	}

	std::cout<< "Copying " << _input << " to " << _output << ", using " << Nentries << " entries." << std::endl;
	CopyFile(_input.c_str(),_output.c_str(),Nentries);

}
#endif

