import tweepy
import json
from kafka import KafkaProducer

# twitter developer keys config
CONSUMER_KEY = 
CONSUMER_SECRET = 
ACCESS_TOKEN =
ACCESS_SECRET = 

# twitter api config
keywords=['penguin']
languages=['en']

# kafka config
bootstrap_servers = 'localhost:9092'
topic = 'twitter'


class Listener(tweepy.StreamListener):

    def __init__(self, kafka_producer, kafka_topic):
        self.producer = kafka_producer
        self.topic = kafka_topic
        self.count = 0
        
    def on_data(self, raw_data):
        try:
            data = json.loads(raw_data)
            # print(data)

            user = data['user']['screen_name']

            # retweet without comment will be counted as original tweet
            # if data['truncated'] == True:
            if 'extended_tweet' in data:
                text = data['extended_tweet']['full_text']
            elif 'retweeted_status' in data:
                origin_text = data['retweeted_status']
                if 'extended_tweet' in origin_text:
                    text = origin_text['extended_tweet']['full_text']
                else:
                    text = origin_text['text']
            else:
                text = data['text']
            
            # remove emoji and '\n' characters in text
            processed_text = text.encode('ascii', 'ignore').decode('ascii').replace('\n', ' ')

            print(user)
            print(processed_text)
            print('=============')
            
            # send stream data to kafka          
            self.producer.send(self.topic, value=processed_text)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
            
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

if __name__ == "__main__":

    # we need an api object to stream
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    # check if authenticate successfully or not
    me = api.me()
    print(me.screen_name)

    # create kafka producer
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    # create stream
    if producer.bootstrap_connected():
        textStreamListener = Listener(producer, topic)
        textStream = tweepy.Stream(auth=api.auth, listener=textStreamListener).filter(track=keywords, languages=languages)


