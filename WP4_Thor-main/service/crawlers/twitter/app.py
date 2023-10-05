from flask import Flask
import json
from kafka import KafkaProducer, KafkaConsumer
import tweepy
import logging
import numpy as np
from elasticsearch import Elasticsearch
from uuid import uuid4
import os


from utils.util import json_reader, extract_indicator_of_compromise

import Tweet_classification

app = Flask(__name__)

TOPIC_NAME = "crawl_TwitterIOC"
KAFKA_SERVER = os.environ['KAFKA_SERVER']
KAFKA_CONSUMER_GROUP = "TwitterClassifier1"
ELASTICSEARCH_SERVER= os.environ['ELASTICSEARCH_SERVER']
ELASTICSEARCH_PASSWORD= os.environ['ELASTICSEARCH_PASSWORD']
INDEX_NAME = 'twitter_stream_latest_version'

# Twitter API credentials
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
bearer_token = "AAAAAAAAAAAAAAAAAAAAAFcqZwEAAAAARH5UUFE0HBGErt%2BpJPrLkWphNSY%3DvtKAzuQHfcoT5FC56PZOApO2R51cyem2ljNl9q1FxxU9NW3oXU"



producer = KafkaProducer(bootstrap_servers = KAFKA_SERVER, api_version = (0, 11, 15))

auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)

api = tweepy.API(auth)

consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers = KAFKA_SERVER, value_deserializer=lambda m: json.loads(m.decode('utf-8')),group_id=KAFKA_CONSUMER_GROUP)


es = Elasticsearch(
    ELASTICSEARCH_SERVER,
    basic_auth=("elastic", ELASTICSEARCH_PASSWORD)
)


if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)
    print(f'created elasticsearch index {INDEX_NAME}')

classifier_instance = Tweet_classification.load()


def delete_rules(result):
    if result['data'] is None:
        return None
    rule_ids=[]
    
    for rule in result['data']:
        rule_ids.append(rule['id'])

    if(len(rule_ids) > 0):
        tweet_listener.delete_rules(rule_ids)
    else:
        print("no rules to delete")
        
def classify_tweet(tweet):
    prediction = classifier_instance.classify_tweet(tweet)
    return prediction


def analyze_data(data):

    data_json = data.decode('utf-8')
    data = json.dumps(json.loads(data_json))
    data_final = json.loads(data)
    #print("data2:", data_final)
    #print("type2:", type(data_final))
    if data_final['data']['lang'] == 'en':
        if data_final['data']['text'] is None or data_final['data']['text'] == '':
            print('data is none')
            return
    
        print('TWEET: ', data_final['data']['text'])
        if classify_tweet(data_final['data']['text']) == 1:
            print(f'RELEVANT - {data_final["data"]["text"]} \n list of IOCs: ')
            ioc_exits, iocs = extract_indicator_of_compromise(data_final)
            if not ioc_exits:
              print('no ioc detected')
              return
            print(iocs)
            id = str(uuid4())
            try: 
              res = es.index(index=INDEX_NAME, id=id, document=iocs)
            except Exception as e:
              print('Error : ', e)
        else:
            print('NOT RELEVANT')
    else:
        print('NOT RELEVANT')




@app.route('/kafka/pushToConsumers', methods=['POST'])
def send_to_broker(json_data):
    
    json_payload = json.dumps(json.loads(json_data.decode()))
    json_payload = str.encode(json_payload)
    
    # push data into INFERENCE TOPIC
    producer.send(TOPIC_NAME, json_payload)
    producer.flush()
    #print("text:",json_payload)
    print('Sent to consumer')
    analyze_data(json_data)
    return


class IOCStreamListener(tweepy.StreamingClient):

    #def on_tweet(self, tweet):
    
        
    def on_data(self, data):
        #print(data)
       # send_to_broker(json.loads(data.decode()))
        send_to_broker(data)
        print("outside1")
        return


if __name__ == "__main__":

    #tweet_listener = IOCStreamListener(consumer_key, consumer_secret, access_token, access_token_secret)
    tweet_listener = IOCStreamListener(bearer_token, return_type=dict,wait_on_rate_limit=True)
    delete_rules(tweet_listener.get_rules())       
    # tweet_listener.filter(track=["ioc","indicator_of_compromise", "maldoc", "spam", "malspam", "threathunting", "blacklist",
    #                              "datasecurity","linux","ransomware","phishing","ethicalhacking","cybersecuritytraining",
    #                              "cybersecurityawareness","malware","informationsecurity","infosec", "threatintel"
    #                              "cybercrip","hacker","cybercrime","cybersecurityengineer","android", "opendir", "osint",
    #                              "ios","networking","cyberattack","kalilinux","anonymous", "cybersecurityengineer"], threaded=True, languages=['en'])
    tweet_listener.add_rules( tweepy.StreamRule("#ioc"))
    tweet_listener.add_rules( tweepy.StreamRule("hxxps://"))
    tweet_listener.add_rules( tweepy.StreamRule("#hxxps"))
    tweet_listener.add_rules( tweepy.StreamRule("#phishing"))
    #tweet_listener.add_rules( tweepy.StreamRule("ioc"))
    #tweet_listener.add_rules(tweepy.StreamRule("lang:en"))
    print(tweepy.StreamingClient.get_rules(tweet_listener))

    #tweet_listener.filter(track=["ioc"], threaded=True, languages=['en'])
    #tweet_listener.filter()
    try:
         tweet_listener.filter(tweet_fields = ["attachments","author_id","context_annotations","conversation_id","created_at","edit_controls","edit_history_tweet_ids","entities","geo","id","in_reply_to_user_id","lang","non_public_metrics","organic_metrics","possibly_sensitive","promoted_metrics","public_metrics","referenced_tweets","reply_settings","source","text","withheld"])
    #tweet_listener.filter(tweet_fields = ["author_id","source","text"])
    except Exception as e:
         print(e)
         
    print("outside")
    for data in consumer:
        print("inside")
        value = data.value
        print('data is received')

        analyze_data(value)

