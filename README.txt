#############################################################
#  Travail de Master de Kim Zaugg, 2021                     #
#  Suivi en temps réel d'événements majeurs sur Twitter     #	
#	 à des fins d'exploitation d'images        	    #
#############################################################

Programme de collecte d'images utilisant les APIs de twitter, version de python 3.9

Avant de commencer :
1. Installer tweepy
2. copier les différents dossiers et fichiers et s'assurer qu'ils soient vides
3. Ecrire les mots-clés à rechercher dans le fichier hashtag.py
4. Enregistrer les clés d'identification à twitter developer dans twitter_credentials.txt
5. Enregistrer les dates de début et de fin de l'événements dans le fichier dates.txt

5 étapes de collecte - 1 test est effectuée à chaque étape en postant des images sur Twitter

1. Collecte en temps réel 						: 	lancer le script 1_streamer.py
2. Collecte à postériori avec les mêmes mots-clés 			: 	lancer le script 2_keywords.py
3. Collecte à postériori avec les utilisateurs 				: 	lancer le script 3_user_post.py
4. Collecte à postériori des threads 					: 	lancer le script 4_thread.py (peut être effectué plusieurs fois à différents intervalles de temps)
5. Collecte à postériori avec les nouveaux mots-clés et hashtags 	: 	lancer le script 5_keywords.py (le fichier hashtag_list.csv peut être complété manuellement avant le lancement si besoin)

Tous les fichiers de résultats et les images/vidéos sont enregistrés dans le dossier resultats.
