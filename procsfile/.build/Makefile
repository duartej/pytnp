CC=gcc
INCDIR=`root-config --incdir`
LIBS=`root-config --libs`


all: copyFile CowboysNTuple

copyFile: copyFile.cpp
	$(CC) -I$(INCDIR) $(LIBS) -o copyFile copyFile.cpp

CowboysNTuple: CowboysNTuple.cpp
	$(CC) -I$(INCDIR) $(LIBS) -o CowboysNTuple CowboysNTuple.cpp


