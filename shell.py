import os, sys

on creer un tube pour faire communiquer les deux processus
os.mkfifo("/tmp/tube", os.O_RDWR |os.O_TRUNC | os.O_CREAT|os.O_EXCL)

# creation du processus
processus=os.fork()
if(processus==0):
	print(" le pid du fils: %d\n" % (os.getpid()))
	#ouvrir le tube en mode ecriture seule , on redirige le rsultat de l'exec vers le tube
	fdTube=os.open("/tmp/tube",os.O_WRONLY)
	# le 1 c'est le descripteur de fichier de la sortie standard
	os.dup2(fdTube,1)	
	os.execl("/bin/ps","ps","aux")
	
else:
	print(" le pid du pere: %d\n" % (os.getpid()))
	# on creer une variable qui contiendra le resultat de la commande et on initialise a une chaine vide
	commandePs=""
	fdTube=os.open("/tmp/tube",os.O_RDONLY)
	# on fait une bouble pour lire le resultat morceau par morceau
	while(True):
		morceau=os.read(fdTube,3) 
		commandePs+=morceau
		# si le morceau est vide : on sort de la boucle car il y a plus rien a lire
 		if not morceau:
			break
	os.close(fdTube)
	print("%d\n", commandePs)
	#suprimer le tube creer
	os.unlink("/tmp/tube")
