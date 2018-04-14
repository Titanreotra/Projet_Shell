import os,sys,time
import lexer as ssp 

#  **** fonction pour excuter*****

def executerCommandeSimple(processus, entreeProcessus=0, sortieProcessus=1):

	(rfd,wfd)=os.pipe() # derscrtiteur de lecture et dectiture de pipe
	pid=os.fork() # 
	if(pid==0): # le fils s'ocuupe de l'excution de la commande
		os.close(rfd)# fermeture de cote lecture du pipe
		commande=processus._cmd.getCommand()
		argCommande=processus._cmd.getArgs()
		print("je vais executer " + commande)
		print("je suis le fils %d" %(os.getpid()))

		redirEntree=filtrerRedirectionsEntree(processus)
		#print(redirEntree)
		if redirEntree:
			#print(redirEntree._filespec)
			re_re_fd=os.open(redirEntree._filespec, os.O_RDONLY)
			#print(re_fd)
			os.dup2(re_re_fd, 0)
		elif entreeProcessus != 0:
			os.dup2(entreeProcessus, 0)


		redirErreur=filtrerRedirectionsErreur(processus)# redirection d'erreur gerer par le fils 
		re_Er_fd=None
		if redirErreur: 
			if redirErreur.isAppend():
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
			else:
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY| os.O_CREAT)

			os.dup2(re_Er_fd,2)	

		os.dup2(wfd,1)# utiliser wfd au lieu de la sortie standard
		argCommande=[commande]+ argCommande # pour tt les fonction exec le 1er argCommande doit etre la commande lui meme

		try: # essaye cette commande 
			os.execv("/bin/"+commande,argCommande)
		except OSError as e:
			if e.errno==2: # si il y a une erreur 
				try:
					log("python3 va executer")
					os.execv("/usr/bin/"+commande,argCommande) # esaye l'autre commande 
				except OSError as e:
					if e.errno==2:
						try:
							os.execv("./"+commande, argCommande)
						except OSError as e:
						
							os.write(2,byteaargCommanderray(e.strerror,"utf-8")) # affiche dans la sortie d'erreur standard
				
			print("coucou")
			
	else: # pere 

		os.close(wfd) # fermeture du cote  ecriture du pipe
		print("j attends le %d\n" %(pid))
		#time.sleep(1)
		(p,es) = os.waitpid(pid,0)
		#print("j'ai fini attendre pour %d qui a %s\n" %(pid,os.WIFEXITED(es)))


		redirSortie=filtrerRedirectionsSortie(processus) # redirection de la sortie gerer par le père
		re_wr_fd=None
		if redirSortie:
			if redirSortie.isAppend():
				re_wr_fd=os.open(redirSortie._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
			else:
				re_wr_fd=os.open(redirSortie._filespec, os.O_WRONLY| os.O_CREAT)

			os.dup2(re_wr_fd,1)
		elif sortieProcessus != 1:
			os.dup2(sortieProcessus,1)


		while True:
			morceau=os.read(rfd,3)
			if not morceau:
				break
			os.write(1, morceau)# ecrit dans la sortie standard 

		os.close(rfd) # fermeture du cote lecture du pipe
		if re_wr_fd:
		 	os.close(re_wr_fd)

def log(msg): # pour voir les erreur sur le code
	log_fd=os.open("log.txt", os.O_CREAT | os.O_WRONLY )
	os.write(log_fd,bytearray(msg,"utf-8"))
	os.close(log_fd)



def filtrerRedirectionsEntree(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "INREDIR"), None)

def filtrerRedirectionsSortie(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "OUTREDIR"), None)

def filtrerRedirectionsErreur(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "ERRREDIR"), None)







if __name__ =='__main__':
	nomPipe="/tmp/pomme"
	pl=ssp.get_parser().parse("sh ficTest2.sh > ghi.txt 2> cerise.txt")
	tubesEnchainement = []
	for i in range(len(pl)):
		tubesEnchainement.append(os.pipe())

	for i in range(len(pl)):
		p = pl[i]
		print(p)

		if i == 0:
			executerCommandeSimple(p, 0, tubesEnchainement[i][1])
		elif i == len(pl)-1:
			executerCommandeSimple(p, tubesEnchainement[i-1][0], 1)
		else:
			executerCommandeSimple(p, tubesEnchainement[i-1][0], tubesEnchainement[i][1])

		#print(filtrerRedirectionsEntree(p))
		#print(filtrerRedirectionsSortie(p))
		#print(filtrerRedirectionsErreur(p))


		executerCommandeSimple(p)


	for i in range(len(pl)):
		os.close(tubesEnchainement[i][0])
		os.close(tubesEnchainement[i][1])
















