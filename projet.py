import os,sys,time
import lexer as ssp 

def executerCommandeSimple(commande, argCommande):

	(rfd,wfd)=os.pipe() # derscrtiteur de lecture et dectiture de pipe
	pid=os.fork() # 
	if(pid==0): # le fils s'ocuupe de l'excution de la commande
		os.close(rfd)# fermeture de cote lecture du pipe
		print("je vais executer " + commande)
		print("je suis le fils %d" %(os.getpid()))
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
			
	else:

		os.close(wfd) # fermeture du cote  ecriture du pipe
		print("j attends le %d\n" %(pid))
		#time.sleep(1)
		(p,es) = os.waitpid(pid,0)
		#print("j'ai fini attendre pour %d qui a %s\n" %(pid,os.WIFEXITED(es)))
		res=""
		while True:
			morceau=os.read(rfd,3)
			if not morceau:
				break
			os.write(1, morceau)# ecrit dans la sortie standard 
		os.close(rfd) # fermeture du cote lecture du pipe






if __name__ =='__main__':
	nomPipe="/tmp/pomme"
	pl=ssp.get_parser().parse("ps -aux | wc -l shell.py")
	for p in pl:
		print(p)
		commande=p._cmd.getCommand()
		argCommande=p._cmd.getArgs()
		executerCommandeSimple(commande, argCommande)
















