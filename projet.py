import os,sys,time
import lexer as ssp 

#  **** fonction pour excuter*****

def executerCommandeSimple(processus):

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


		os.dup2(wfd,1)# utiliser wfd au lieu de la sortie standard
		argCommande=[commande]+ argCommande # pour tt les fonction exec le 1er argCommande doit etre la commande lui meme

		try: # essaye cette commande 
			os.execv("/bin/"+commande,argCommande)
		except OSError as e:
			if e.errno==2: # si il y a une erreur 
				try:
					os.execv("/usr/bin/"+commande,argCommande) # esaye l'autre commande 
				except OSError as e:
					os.write(2,bytearray(e.strerror)) # affiche dans la sortie d'erreur standard
				
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


		redirErreur=filtrerRedirectionsErreur(processus)# redirection d'erreur gerer par le père
		print(redirErreur)
		re_Er_fd=None
		if redirErreur: 
			if redirErreur.isAppend():
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
			else:
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY| os.O_CREAT)

			os.dup2(re_Er_fd,2)	

		while True:
			morceau=os.read(rfd,3)
			if not morceau:
				break
			os.write(1, morceau)# ecrit dans la sortie standard 

		os.close(rfd) # fermeture du cote lecture du pipe
		# if re_wr_fd:
		# 	os



def filtrerRedirectionsEntree(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "INREDIR"), None)

def filtrerRedirectionsSortie(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "OUTREDIR"), None)

def filtrerRedirectionsErreur(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "ERRREDIR"), None)







if __name__ =='__main__':
	nomPipe="/tmp/pomme"
	pl=ssp.get_parser().parse("ps -aux > sortie.txt 2> erreur.txt   | wc -l < shell.py >> shellLongueur.txt | python3 fictest.py 2> cerise.txt")
	for p in pl:
		print(p)
		#print(filtrerRedirectionsEntree(p))
		#print(filtrerRedirectionsSortie(p))
		#print(filtrerRedirectionsErreur(p))


		executerCommandeSimple(p)
















