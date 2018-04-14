import os, sys


if __name__ =='__main__':

	os.read(0,10)
	os.write(1,b"coucou")
	os.write(2,b"il y a une erreur")