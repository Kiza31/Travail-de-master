#############################################################
#  Travail de Master de Kim Zaugg, 2021                     #
#  Suivi en temps réel d'événements majeurs sur Twitter 	#
#  à des fins d'exploitation d'images        				#
#############################################################


'''
script qui va rechercher les threads (à postériori) dans les posts collectés en temps réel
'''

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import sys

import urllib.request
import re, csv
import time

import json
import datetime


with open("parametres/credentials.txt") as credentials:
    credentials = credentials.readlines()[0:]

    CONSUMER_KEY = credentials[0][16:41]
    CONSUMER_SECRET = credentials[1][19:69]
    ACCESS_TOKEN = credentials[2][16:66]
    ACCESS_TOKEN_SECRET = credentials[3][23:68]

auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def get_all_tweets(tweet):
    screen_name = tweet.user.screen_name
    lastTweetId = tweet.id
    #initialize a list to hold all the tweepy Tweets
    allTweets = []
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200, wait_on_rate_limit= True)
    allTweets.extend(new_tweets)
    #save the id of the oldest tweet less one
    oldest = allTweets[-1].id - 1
    #keep grabbing tweets until there are no tweets left to grab --> Prend beaucoup trop de temps car fait trop tard pour la ZAD !

    while len(new_tweets) > 0 and oldest >= lastTweetId:
        print(f"getting tweets before {oldest}")
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, wait_on_rate_limit= True)
        #save most recent tweets
        allTweets.extend(new_tweets)
        #update the id of the oldest tweet less one
        oldest =allTweets[-1].id - 1
        print(f"...{len(allTweets)} tweets downloaded so far")

    outtweets = [tweet.id for tweet in allTweets]
    return outtweets

def getAllTweetsInThreadAfterThis(tweetId):
    thread = []
    hasReply = True
    res = api.get_status(tweetId, tweet_mode='extended', wait_on_rate_limit= True)
    with open("ressources/thread_search.txt", 'a', encoding="utf-8") as tf:
        tf.write(str(res) + "\n\n")
    #print (res)
    allTillThread = get_all_tweets(res)
    thread.append(res)
    if allTillThread[-1] > res.id:
        print("Not able to retrieve so older tweets")
        return thread
    print("downloaded required tweets")
    startIndex = allTillThread.index(res.id)
    print("Finding useful tweets")
    quietLong = 0
    while startIndex!=0 and quietLong<25:
        nowIndex = startIndex-1
        nowTweet = api.get_status(allTillThread[nowIndex], tweet_mode='extended', wait_on_rate_limit= True)
        if nowTweet.in_reply_to_status_id == thread[-1].id:
            quietLong = 0
            #print("Reached a useful tweet to be included in thread")
            thread.append(nowTweet)
        else:
            quietLong = quietLong + 1
        startIndex = nowIndex
    return thread

def getAllTweetsInThreadBeforeThis(tweetId):
    thread = []
    hasReply = True
    res = api.get_status(tweetId, tweet_mode='extended', wait_on_rate_limit= True)
    while res.in_reply_to_status_id is not None:
        res = api.get_status(res.in_reply_to_status_id, tweet_mode='extended', wait_on_rate_limit= True)
        thread.append(res)
    return thread[::-1]

def getAllTweetsInThread(tweetId):
    tweetsAll = []
    print("Getting all tweets before this tweet")
    tweetsAll = getAllTweetsInThreadBeforeThis(tweetId)
    print(len(tweetsAll))
    print("Getting all tweets after this tweet")
    tweetsAll.extend(getAllTweetsInThreadAfterThis(tweetId))
    return tweetsAll

def printAllTweet(tweets):
    if len(tweets)>0:
        print (len(tweets))
        k=0
        while k < len(tweets) :
            entities_dict = tweets[k].entities
            getmedia = entities_dict.get("media")

            if getmedia :
                with open("ressources/thread_search.txt", 'a', encoding="utf-8") as tf:
                    tf.write(str(tweets[k]) + "\n\n")

                str_id = "ID : " + str(tweets[k].id)
                date_time = tweets[k].created_at
                screen_name = tweets[k].user.screen_name
                text = tweets[k].full_text

                cvsfile = open('resultats/thread_search.csv', 'a', encoding="UTF-8", newline="")
                writer = csv.writer(cvsfile, delimiter=';', dialect='excel')
                writer.writerow([str_id, screen_name, date_time, text])
                cvsfile.close()


                dict_media = tweets[k].entities['media'][0]
                url = dict_media["media_url"]
                n=1
                with open("ressources/media_url.txt") as url_read:
                    if url in url_read.read() :
                        print ("Picture already collected")
                        k+=1
                    else :
                        url_read.close()
                        with open ("ressources/media_url.txt", "a") as url_write:
                            url_write.write(url + "\n")
                            str_n = str(n)
                            storage = "resultats/images_thread/" + str(tweets[k].id) + "_" + str_n + ".jpg"
                            urllib.request.urlretrieve(url, storage)
                            print ("New picture downloaded")
                            n+=1

                            if "video" in url :
                                print ("ce tweet contient une vidéo")

                                ext_ent_dict = tweets[k].extended_entities['media'][0]
                                dict_video_info = ext_ent_dict.get("video_info")
                                dict_variants = dict_video_info.get("variants")[0]
                                url_video = dict_variants.get("url")

                                time.sleep(3)
                                with open("ressources/video_url.txt") as url_read:
                                    if url_video in url_read.read() :
                                        break
                                    else :
                                        url_read.close()
                                        with open ("ressources/video_url.txt", "a") as url_write:
                                            url_write.write(url_video + "\n")
                                            storage = "resultats/video_thread/" + str(tweets[k].id) + ".mp4"
                                            urllib.request.urlretrieve(url_video, storage)
                                            print ("Nouvelle vidéo enregistrée")
                                            break
                            else :
                                k+=1



            else :
                print ("No picture in this tweet")
                k+=1
                pass

    else:
        print("No Tweet to print")

if __name__ == '__main__':

    cvsfile = open('ressources/for_thread.csv', 'r', encoding="UTF-8", newline="")
    reader = csv.reader(cvsfile, delimiter=';', dialect='excel')
    for row in reader :
        tweetid = row[0]
        myTweetId = tweetid[5:]
        print (myTweetId)
        try :
            allTweets = getAllTweetsInThread(myTweetId)
            printAllTweet(allTweets)
            print ("------------------------------")
        except tweepy.TweepError :
            print ("no tweet available with this ID")
            print ("------------------------------")
