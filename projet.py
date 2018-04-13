import os,sys,time

def executerCommandeSimple(nomPipe, commande, argCommande):
	pid=os.fork()
	if(pid==0):
		print("je vais executer " + commande)
		print("je suis le fils %d" %(os.getpid()))
		fd=os.open(nomPipe, os.O_WRONLY|os.O_CREAT)
		os.dup2(fd,1)
		try:
			os.execv("/bin/"+commande,argCommande)
		except OSError,e:
			print("coucou")
			os.write(1,"Daniel")
			os.write(1,e.filename + " manque")
	else:	
		#pass
		print("j attends le %d\n" %(pid))
		#time.sleep(1)
		(p,es) = os.waitpid(pid,0)
		#print("j'ai fini attendre pour %d qui a %s\n" %(pid,os.WIFEXITED(es)))

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
	


if __name__ =='__main__':
	nomPipe="/tmp/pomme"
	try:
		#pass
		os.mkfifo(nomPipe)
	except OSError, e:
		if e.errno == 17:
			print(e.strerror)
	commande="ps"
	argCommande=["-e","-a","-x"]
	executerCommandeRedi(nomPipe,"more shell.py > def.txt",argCommande)
	print("je vais affichier res final")
	afficherResultatFinal(nomPipe)
	#os.unlink(nomPipe)
















