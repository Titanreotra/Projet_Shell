import os,sys,time
import lexer as ssp 

#  **** fonction pour excuter*****

def executerCommandeSimple(processus):
	pid=os.fork() # 
	if(pid==0): # le fils s'ocuupe de l'excution de la commande
		commande=processus._cmd.getCommand()
		argCommande=processus._cmd.getArgs()
		redirEntree=filtrerRedirectionsEntree(processus)
		
		if redirEntree:
			#print(redirEntree._filespec)
			re_re_fd=os.open(redirEntree._filespec, os.O_RDONLY)
			os.dup2(re_re_fd, 0)
			os.close(re_re_fd)

		re_wr_fd=None
		redirSortie=filtrerRedirectionsSortie(processus) # redirection de la sortie gerer par le pere
		# print('r')
		# print(redirSortie)
		if redirSortie:
			# os.write(2, b'red sortie')
			if redirSortie.isAppend():
				re_wr_fd=os.open(redirSortie._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_TRUNC)
			else:
				re_wr_fd=os.open(redirSortie._filespec, os.O_WRONLY| os.O_CREAT | os.O_TRUNC)


			os.dup2(re_wr_fd,1)

			# os.close(re_wr_fd)
		else: 
			pass
			# os.write(2,b'Pas de redirSortie')


		

		redirErreur=filtrerRedirectionsErreur(processus)# redirection d'erreur gerer par le fils 
		re_Er_fd=None
		if redirErreur: 
			if redirErreur.isAppend():
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
			else:
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY| os.O_CREAT)
			# os.write(2, b'rediriger erreur')
			os.dup2(re_Er_fd,2)	

		#os.dup2(wfd,1)# utiliser wfd au lieu de la sortie standard
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
						
							os.write(2,bytearray(argCommanderray(e.strerror,"utf-8"))) # affiche dans la sortie d'erreur standard
				
			
	else: # pere 

		# print("j attends le %d\n" %(pid))
		(p,es) = os.waitpid(pid,0)
		# print("j'ai fini attendre pour %d qui a %s\n" %(pid,os.WIFEXITED(es)))



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
	pl=ssp.get_parser().parse("sh imp.sh > sortie.txt | sh imp.sh 2> cerise.txt | wc -c < cerise.txt  ")
	# pl = ssp.get_parser().parse("sh ficTest2.sh > ghi.txt 2> cerise.txt")
	for p in pl:
		# print(p)
		#print(filtrerRedirectionsEntree(p))
		#print(filtrerRedirectionsSortie(p))
		#print(filtrerRedirectionsErreur(p))


		executerCommandeSimple(p)
















