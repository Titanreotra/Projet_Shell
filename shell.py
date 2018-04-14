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



def copierVersPipe(nomPipe,nomFichier):
	print("on va copier vers pipe")
	fdf=os.open(nomFichier, os.O_RDONLY)
	fdp=os.open(nomPipe,os.O_RDWR|os.O_CREAT|os.O_TRUNC)
	print("pipe ouvert pour copier")
	while(True):
		morceau=os.read(fdf,65)
		morceau = morceau.strip()
		if morceau=="":
			break	
		#print("morceau lu " + morceau)
		os.write(fdp,morceau)
	os.close(fdf)
	os.close(fdp)
	print("fini copier vers pipe")

def copierVersFichier(nomPipe, nomFichier):
	fdp=os.open(nomPipe,os.O_RDONLY | os.O_NONBLOCK)
	fdf=os.open(nomFichier,os.O_WRONLY|os.O_TRUNC)
	while(True):
		morceau= "x"
		try :
			morceau=os.read(fdp,13)
		except OSError, e:
			print(e.strerror)
		if not morceau:
			break
		os.write(fdf,morceau)
		
	os.close(fdf)
	os.close(fdp)
	print("fini copier vers fichier")

	
	


def executerCommandeRedi(nomPipe, commande, argCommande):
	commandeCouper=commande.split(">")
	commandeSimple=commandeCouper[0].strip()
	commandeSimpleArgs = commandeSimple.split(' ')
	executerCommandeSimple(nomPipe, commandeSimpleArgs[0], commandeSimpleArgs)
	for i in range(1,len(commandeCouper)):
		copierVersFichier(nomPipe,commandeCouper[i].strip())
		os.unlink(nomPipe)
		os.mkfifo(nomPipe)
		copierVersPipe(nomPipe,commandeCouper[i].strip())	

def afficherResultatFinal(nomPipe):
	fdp=os.open(nomPipe,os.O_RDONLY| os.O_NONBLOCK)
	resultat=""
	while(True):
		morceau=os.read(fdp,33)
		if not morceau:
			break 
		resultat+=morceau
		# si le morceau est vide : on sort de la boucle car il y a plus rien a lire
 		
	os.close(fdp)
	print("x%sx\n" %(resultat))
	