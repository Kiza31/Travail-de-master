#############################################################
#  Travail de Master de Kim Zaugg, 2021                     #
#  Suivi en temps réel d'événements majeurs sur Twitter 	#
#  à des fins d'exploitation d'images        				#
#############################################################


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import ssl
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError



import urllib.request
import re, csv
import time

import hashtag

import datetime


# Add your Twitter API credentials
with open("parametres/credentials.txt") as credentials:
    credentials = credentials.readlines()[0:]

    CONSUMER_KEY = credentials[0][16:41]
    CONSUMER_SECRET = credentials[1][19:69]
    ACCESS_TOKEN = credentials[2][16:66]
    ACCESS_TOKEN_SECRET = credentials[3][23:68]

    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create a wrapper for the API provided by Twitter
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

hashtaglist = hashtag.HASH_TAG_LIST
for i in hashtaglist :
    keyword = i
    with open("parametres/dates.txt") as dates:
        date = dates.readlines()[1:]
        deb = date[0]
        fin = date[1]
        annee_deb = int(deb[17:21])
        mois_deb = int (deb[22:24])
        jour_deb = int (deb[25:27])
        annee_fin = int (fin[14:18])
        mois_fin = int (fin[19:21])
        jour_fin= int (fin[22:24])
        date_deb = datetime.date(annee_deb, mois_deb, jour_deb)
        date_fin = datetime.date(annee_fin, mois_fin, jour_fin)

    cursor = tweepy.Cursor(api.search, q=keyword, tweet_mode="extended", since=date_deb, until=date_fin).items()
    for i in cursor :
        tweet = str(i) + "\n\n"
        if 'RT @' not in tweet :
            if 'media_url' in tweet :
                with open("ressources/hashtag_search.txt", 'a', encoding="utf-8") as tf:
                    tf.write(tweet) #ouvre et enregistre les donnees dans un fichier .txt
                    #print(tweet, "\n")
                    '''
                    identifier l'id du tweet, la date/heure, le texte et la localisation
                    '''
                    id = tweet[120:139]
                    tweet_id = "ID : " + id

                    date = tweet[85:91] + " " + tweet[107:111]
                    heure = tweet[92:100]
                    utc = "UTC +" + tweet[102:106]
                    text = ""
                    i=183
                    for symb in tweet :
                        textbreak = tweet[i:i+16]
                        if textbreak == "', 'truncated': " :
                            text = tweet[183:i]
                            break
                        else :
                            i+=1
                    k=0
                    for symb in tweet :
                        starter = tweet[k:k+19]
                        if starter == "', 'screen_name': '" :
                            l=k+19
                            for symb in tweet :
                                breaker = tweet[l:l+16]
                                if breaker =="', 'location': '" :
                                    username = tweet [k+19:l]
                                    print (username)

                                    with open("ressources/username.txt", 'r') as user_read:
                                        if username in user_read.read() :
                                            with open("ressources/username_2.csv") as user2_read :
                                                if username in user2_read.read() :
                                                    pass
                                                else :
                                                    user2_read.close()
                                                    with open("ressources/username_2.csv", 'a') as user2_write :
                                                        user2_write.write(username + "\n")
                                        else :
                                            user_read.close()
                                            with open("ressources/username.txt", 'a') as user_write:
                                                user_write.write(username + "\n")

                                    break
                                else :
                                    l+=1
                            break
                        else :
                            k+=1

                    long = len(text)
                    i=0
                    j=0
                    while i < long :
                        if text[i:i+1] == "#" :
                            text_rest = text[i:]
                            end = text_rest.find(" ")
                            hashtag = text_rest[:end]
                            '''
                            enregistré les hashtags dans un fichier .csv
                            '''
                            cvsfile = open('resultats/hashtag_list.csv', 'a', encoding="UTF-8", newline="")
                            writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                            writer.writerow([tweet_id, hashtag])
                            cvsfile.close()

                            i+=1
                        else :
                            i+=1

                    '''
                    enregistrer dans un fichier .csv ID, date/heure/UTC, localisation, username, texte
                    '''
                    cvsfile = open('resultats/hashtag_search.csv', 'a', encoding="UTF-8", newline="")
                    writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                    writer.writerow([tweet_id, username, date, heure, utc, text])
                    cvsfile.close()

                    cvsfile = open('ressources/for_thread.csv', 'a', encoding="UTF-8", newline="")
                    writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                    writer.writerow([tweet_id])
                    cvsfile.close()

                    print ("Nouvel enregistrement")




                    '''
                    Télécharger la photo et l'enregistrer dans un dossier
                    '''

                    str_id = str(id)
                    n=1
                    i=0
                    for symb in tweet :
                        chainestart = tweet[i : i+14]
                        if chainestart == "'media_url': '" :
                            j = i+14
                            for symb in tweet :
                                chainebreak1 = '.jpg'
                                chainebreak2 = '.png'
                                if tweet [j:j+4] == chainebreak1 or tweet [j:j+4] == chainebreak2 :
                                    url = tweet[i+14:j+4]
                                    print (url)
                                    with open("ressources/media_url.txt") as url_read:
                                        if url in url_read.read() :
                                            n+=1
                                            i=j+4
                                            break
                                        else :
                                            url_read.close()
                                            with open ("ressources/media_url.txt", "a") as url_write:
                                                url_write.write(url + "\n")
                                                str_n = str(n)
                                                print ("OK")
                                                storage = "resultats/images_keyword_1/" + str_id + "_" + str_n + ".jpg"
                                                urllib.request.urlretrieve(url, storage)
                                                print ("Nouvelle image enregistrée")

                                                n+=1
                                                i=j+4
                                                if "video" in url :
                                                    print ("ce tweet contient une vidéo")
                                                    i=0
                                                    for symb in tweet :
                                                        chainestart = tweet[i : i+14]
                                                        if chainestart == "mp4', 'url': '" :
                                                            j = i+14
                                                            for symb in tweet :
                                                                chainebreak = '.mp4'
                                                                if tweet [j:j+4] == chainebreak :
                                                                    video_url = tweet[i+14:j+4]
                                                                    video_url = video_url.replace("\/","/")
                                                                    print(video_url)
                                                                    time.sleep(3)
                                                                    with open("ressources/video_url.txt") as url_read:
                                                                        if video_url in url_read.read() :
                                                                            i=j+10
                                                                            break
                                                                        else :
                                                                            url_read.close()
                                                                            with open ("ressources/video_url.txt", "a") as url_write:
                                                                                url_write.write(video_url + "\n")
                                                                                storage = "resultats/video_keyword_1/" + str_id + ".mp4"
                                                                                urllib.request.urlretrieve(video_url, storage)
                                                                                print ("Nouvelle vidéo enregistrée")
                                                                                i=j+4
                                                                                break

                                                                else :
                                                                    j+=1
                                                        else :
                                                            i+=1
                                                else :
                                                    break
                                else :
                                    j+=1
                        else :
                            i+=1
            else :
                pass

        else :
            pass
