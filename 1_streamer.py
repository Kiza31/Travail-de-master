#############################################################
#  Travail de Master de Kim Zaugg, 2021                     #
#  Suivi en temps réel d'événements majeurs sur Twitter 	#
#  à des fins d'exploitation d'images        				#
#############################################################


'''
programme de principal pour le streaming de tweets. Ne rien modifier ici !!
'''


from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import urllib.request
import re, csv
import time

import hashtag

import datetime

class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        pass

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        with open("parametres/credentials.txt") as credentials:
            credentials = credentials.readlines()[0:]

            CONSUMER_KEY = credentials[0][16:41]
            CONSUMER_SECRET = credentials[1][19:69]
            ACCESS_TOKEN = credentials[2][16:66]
            ACCESS_TOKEN_SECRET = credentials[3][23:68]
        listener = StdOutListener(fetched_tweets_filename)

        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        stream = Stream(auth, listener)

        stream.filter(track=hashtag.HASH_TAG_LIST)

class StdOutListener(StreamListener):
    '''
    permet d'écouter
    '''
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):

        try:

            if 'RT @' not in data :
                    with open(self.fetched_tweets_filename, 'a') as tf:
                        tf.write(data + "\n\n") #ouvre et enregistre les donnees dans un fichier .txt

                    '''
                    identifier l'id du tweet, le username, la date/heure, le texte et la localisation
                    '''
                    id = data[52:71]
                    tweet_id = "ID : " + id

                    i = 0
                    screenname = ""
                    for symb in data :
                        chainestart = data[i : i+15]
                        if chainestart == '"screen_name":"' :
                            j = i
                            for symb in data :
                                chainebreak = data[j : j+13]
                                if chainebreak == '","location":' :
                                    screenname = data[i+15:j]
                                    print ("---------------\n", screenname, "   :   ")
                                    break
                                else :
                                    j+=1
                            break
                        else :
                            i+=1
                    '''
                    enregistrer le screen_name dans un fichier, s'il y est déjà, l'enregistré dans un deuxième, s'il y est déjà, pass
                    '''


                    with open("ressources/username.txt", 'r') as user_read:
                        if screenname in user_read.read() :
                            with open("ressources/username_2.csv") as user2_read :
                                if screenname in user2_read.read() :
                                    pass
                                else :
                                    user2_read.close()
                                    with open("ressources/username_2.csv", 'a') as user2_write :
                                        user2_write.write(screenname + "\n")
                        else :
                            user_read.close()
                            with open("ressources/username.txt", 'a') as user_write:
                                user_write.write(screenname + "\n")



                    #texte
                    text = ""
                    for symb in data :
                        if '"full_text":"' in data :
                            chainestart = '"full_text":"'
                            i = data.find(chainestart)
                            j = i+13
                            for symb in data :
                                chainebreak = data[j : j+3]
                                if chainebreak == '","' :
                                    text = data[i+13:j]
                                    print (text, "\n")
                                    break
                                else :
                                    j+=1
                            break
                        elif '","text":"' in data :
                            chainestart = '","text":"'
                            i = data.find(chainestart)
                            j = i+10
                            for symb in data :
                                chainebreak = data[j : j+3]
                                if chainebreak == '","' :
                                    text = data[i+10:j]
                                    print (text, "\n")

                                    break
                                else :
                                    j+=1
                            break
                        else :
                            break
                    #date/heure/UTC
                    date = data[19:25] + " " + data[41:45]
                    heure = data[26:34]
                    UTC = "UTC " + data[35:40]
                    #localisation
                    i = 0
                    user_location = ""
                    for symb in data :
                        chainestart = data[i : i+14]
                        if chainestart == '","location":"' :
                            start = i+14
                            j = i
                            for symb in data :
                                chainebreak = data[j : j+8]
                                if chainebreak == '","url":'  :
                                    user_location = data[start:j]
                                    break
                                else :
                                    j+=1
                            break
                        else :
                            i+=1

                    '''
                    recherche des hashtags dans le texte
                    '''
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




                    cvsfile = open('ressources/for_thread.csv', 'a', encoding="UTF-8", newline="")
                    writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                    writer.writerow([tweet_id])
                    cvsfile.close()

                    '''
                    Télécharger la photo et l'enregistrer dans un dossier
                    '''
                    str_id = str(id)
                    n=1
                    i=0
                    for symb in data :
                        chainestart = data[i : i+14]
                        if chainestart == ',"media_url":"' :
                            j = i+14
                            for symb in data :
                                chainebreak1 = '.jpg'
                                chainebreak2 = ".png"
                                if data [j:j+4] == chainebreak1 or data [j:j+4] == chainebreak2 :
                                    media_url = data[i+14:j+4]
                                    url = media_url.replace("\/","/")
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
                                            storage = "resultats/images_stream/" + str_id + "_" + str_n + ".png"
                                            urllib.request.urlretrieve(url, storage)
                                            print ("Nouvelle image enregistrée")
                                            n+=1
                                            i=j+4

                                            '''
                                            enregistrer l'url de la video
                                            '''
                                            if "video" in url :
                                                print ("ce tweet contient une vidéo")
                                                i=0
                                                for symb in data :
                                                    chainestart = data[i : i+12]
                                                    if chainestart == 'mp4","url":"' :
                                                        j = i+12
                                                        for symb in data :
                                                            chainebreak = '.mp4'
                                                            if data [j:j+4] == chainebreak :
                                                                video_url = data[i+12:j+4]
                                                                video_url = video_url.replace("\/","/")
                                                                with open("ressources/video_url.txt") as url_read:
                                                                    if video_url in url_read.read() :
                                                                        i=j+10
                                                                        break
                                                                    else :
                                                                        url_read.close()
                                                                        with open ("ressources/video_url.txt", "a") as url_write:
                                                                            url_write.write(video_url + "\n")

                                                                        storage = "resultats/video_stream/" + str_id + ".mp4"
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

                    new_pictures = str(n-1) + " image(s)"
                    cvsfile = open('resultats/data_stream.csv', 'a', encoding="UTF-8", newline="")
                    writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                    writer.writerow([tweet_id, screenname, date, heure, UTC, user_location, text, new_pictures])
                    cvsfile.close()
                    return True

            else :
                pass

        except BaseException as e:
            print("Error on_data %s" % str(e))
            return True


    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    # Authenticate using config.py and connect to Twitter Streaming API.
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    fetched_tweets_filename = "ressources/stream_" + date + ".txt"
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename, hashtag.HASH_TAG_LIST)
