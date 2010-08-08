/*
   copyFile.cpp

   copies the contents of a File, but only
   the number of events specified as input.

Compilation: gcc `root-config --libs` -I`root-config --incdir` -o copyFile copyFile.cpp

Arguments: * Number of events to copy (default all)
           * Name of the output dataset


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

#include "TDirectory.h"
#include "TROOT.h"
#endif

#include "TKey.h"
#include "TFile.h"
#include "TSystem.h"
#include "TTree.h"
#include <exception>

      
void CopyDir(TDirectory *source, int NumEntries) {
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
		  	CopyDir(subdir,NumEntries);
		  	adir->cd();
	    	} 
		else if (cl->InheritsFrom(TTree::Class())) 
		{
		  	TTree *T = (TTree*)source->Get(key->GetName());
		  	adir->cd();
		  	TTree *newT = T->CloneTree(NumEntries,"fast");
		  	newT->Write();
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
      	CopyDir(finput,NumEntries);
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
		std::cout << "    -n NumEntries " << std::endl;
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
			if( strcmp(argv[i],"-n") == 0 )
			{
				Nentries = atoi(argv[i+1]);
				isN = true;
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



