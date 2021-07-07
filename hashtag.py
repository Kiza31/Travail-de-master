#############################################################
#  Travail de Master de Kim Zaugg, 2021                     #
#  Suivi en temps réel d'événements majeurs sur Twitter 	#
#  à des fins d'exploitation d'images        				#
#############################################################


'''
liste à remplir sous la forme : ["un mot clé", "un deuxième", "..."]
'''

HASH_TAG_LIST = [""]

'''
ne tient pas compte des # ni des @ devant le mot clé
ne tient pas compte des majuscules
tient compte des accents
si le mot clé est une partie d'un mot d'un tweet, il ne le ressort (exemple : mot clé "mot" --> ne ressort pas les tweets contenant "mots" )
si plusieurs mots dans un mot-clé, il ressort si tous les mots sont dans le tweet, peut importe l'ordre
'''
