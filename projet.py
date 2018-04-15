import os,sys,time
import lexer as ssp 

#  **** fonction pour excuter*****

rfd = None
wfd = None

def executerCommandeSimple(processus, entreeProcessus=0, sortieProcessus=1, sortiePrec = None, num = 0):
	# (rfd,wfd)=os.pipe() # derscrtiteur de lecture et dectiture de pipe


	pid=os.fork() # 
	if(pid==0): # le fils s'ocuupe de l'excution de la commande
		commande=processus._cmd.getCommand()
		argCommande=processus._cmd.getArgs()
		redirEntree=filtrerRedirectionsEntree(processus)
		
		if redirEntree:
			#print(redirEntree._filespec)
			re_re_fd=os.open(redirEntree._filespec, os.O_RDONLY)
			os.dup2(re_re_fd, 0, False)

			# os.close(re_re_fd)
		elif entreeProcessus != 0 :
			log("je vais fermer sortieProcessus")
			# os.close(sortiePrec)
			afficherErreur("lire depuis " + str(entreeProcessus) + " au lieu de 0 pour " + commande)
			os.dup2(entreeProcessus, 0)
			# os.close(entreeProcessus)
			# os.close(sortieProcessus)

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
		elif sortieProcessus != 1:

			afficherErreur('ecrire dans ' + str(sortieProcessus) + ' au lieu de 1 pour ' + processus._cmd.getCommand())
			os.dup2(sortieProcessus,1)
		# 	os.close(entreeProcessus)
			# os.close(sortieProcessus)
		
			# os.close(entreeProcessus)

		redirErreur=filtrerRedirectionsErreur(processus)# redirection d'erreur gerer par le fils 
		re_Er_fd=None
		if redirErreur: 
			if redirErreur.isAppend():
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
			else:
				re_Er_fd=os.open(redirErreur._filespec, os.O_WRONLY| os.O_CREAT)
			# os.write(2, b'rediriger erreur')
			os.dup2(re_Er_fd,2)	

		if sortiePrec:
			os.close(sortiePrec)
			# afficherErreur('mmimimi ' +str(sortiePrec))

		
		#os.dup2(wfd,1)# utiliser wfd au lieu de la sortie standard
		argCommande=[commande]+ argCommande # pour tt les fonction exec le 1er argCommande doit etre la commande lui meme

		try: # essaye cette commande 
			afficherErreur("va execut " + commande)
			os.execv("/bin/"+commande,argCommande)
		except OSError as e:
			if e.errno==2: # si il y a une erreur 
				try:
					afficherErreur( commande +" va executer")
					os.execv("/usr/bin/"+commande,argCommande) # esaye l'autre commande 
				except OSError as e:
					afficherErreur(e.strerror)
					if e.errno==2:
						try:
							afficherErreur( commande +" va executer 3")

							os.execv("./"+commande, argCommande)
						except OSError as e:
							afficherErreur("commande echoue")
							os.write(2,byteaargCommanderray(e.strerror,"utf-8")) # affiche dans la sortie d'erreur standard
				
			
	else: # pere 
		# os.close(wfd) # fermeture du cote  ecriture du pipe
		#afficherErreur("j attends le %d %s\n " %(pid, processus._cmd.getCommand()))
		#time.sleep(1)
		(p,es) = os.waitpid(pid,0)
		#afficherErreur("j'ai fini attendre pour %d qui a %s\n" %(pid,os.WIFEXITED(es)))


						
				


def log(msg): # pour voir les erreur sur le code
	log_fd=os.open("log.txt", os.O_CREAT | os.O_WRONLY | os.O_APPEND )
	os.write(log_fd,bytearray(msg + '\n',"utf-8"))
	os.close(log_fd)

def afficherErreur(msg):
	os.write(2, bytearray(msg+'\n',"utf-8"))


def filtrerRedirectionsEntree(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "INREDIR"), None)

def filtrerRedirectionsSortie(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "OUTREDIR"), None)

def filtrerRedirectionsErreur(processus):
	return  next((re for re in processus._redirs._redirs if re.__class__.__name__ == "ERRREDIR"), None)



if __name__ =='__main__':
	pl=ssp.get_parser().parse("sh imp.sh | sh pomme.sh | wc -c > sortie.txt  ")
	tubesEnchainement = []
	for i in range(len(pl)):
		#tubesEnchainement.append(os.pipe())

		pass

	# rfd, wfd = os.pipe()

	# rfd = os.open("tube1.txt", os.O_RDONLY  )
	# wfd = os.open("tub2.txt", os.O_WRONLY | )

	even = True
	for i in range(len(pl)):
		p = pl[i]
		# print(p)

		num = i

		if(num):
			rfd = os.open("tube" + str(num-1) + ".txt", os.O_RDONLY )
		wfd = os.open("tube" + str(num) + ".txt", os.O_WRONLY|os.O_CREAT | os.O_TRUNC)

		if(len(pl) == 0):
			executerCommandeSimple(p)

		elif i == 0:
			executerCommandeSimple(p, 0, wfd)
			#os.close(tubesEnchainement[i][1])
		elif i == len(pl)-1:
			executerCommandeSimple(p, rfd, 1)
			# os.close(tubesEnchainement[i][1])
			#os.close(tubesEnchainement[i-1][0])
		else:
			# executerCommandeSimple(p, tubesEnchainement[i-1][0], tubesEnchainement[i][1], tubesEnchainement[i-1][1])
			executerCommandeSimple(p, rfd, wfd)
			# os.close(tubesEnchainement[i-1][0])
			# os.close(tubesEnchainement[i-1][1])

		if num:
			os.close(rfd)
			os.close(wfd)

	# os.close(rfd)
	# os.close(wfd)


















