import tweepy
import json
from kafka import KafkaProducer
from configparser import ConfigParser
from app import auth_keys


class TwitterAuthProvider():

    def getAuth(self):
        consumer_key = auth_keys.CONSUMER_KEY
        consumer_secret = auth_keys.CONSUMER_SECRET
        access_token = auth_keys.ACCESS_TOKEN
        access_secret = auth_keys.ACCESS_TOKEN_SECRET
        print(consumer_key)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth


class Listener(tweepy.StreamListener):

    def __init__(self, kafka_producer, topic_name):
        self.producer = kafka_producer
        self.topic_name = topic_name
        self.count = 0

    def on_data(self, raw_data):
        try:
            self.process_data(raw_data)
            return True
        except BaseException as e:
            print("Error for on-data: %s" % str(e))
        return True

    def process_data(self, raw_data):
        if self.topic_name == "hashtag":
            self.collect_hashtags(raw_data)
        elif self.topic_name == "mention":
            self.collect_mentions(raw_data)

    def collect_hashtags(self, raw_data):
        data = json.loads(raw_data)
        if "text" in data:
            text = data["text"]
        # if "extended_tweet" in data:
        #     text = data["extended_tweet"]["full_text"]
            if '#' in text:
                self.producer.send(self.topic_name, value={"text": text})
                self.count += 1
                if self.count % 100 == 0:
                    print("Number of tweets sent = ", self.count)

    def collect_mentions(self, raw_data):
        print(raw_data)

    def on_error(self, status_code):
        if status_code == 420:
            print("420 Error!")
            # returning False in on_error disconnects the stream
            return False


class StreamTweets():

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth, listener)

    def start(self, location, language, track_keywords):
        self.stream.filter(languages=language,
                           track=track_keywords, is_async=True)

    def track_by_location(self, location, language, track_keywords):
        self.stream.filter(languages=language,
                           track=track_keywords, locations=location)


if __name__ == "__main__":

    config = ConfigParser()
    config.read("../conf/config.conf")
    # config.read("..\conf\config.conf")

    # bootstap_server = config['Kafka_param']['bootstrap.servers']

    bootstrap_server = "localhost:9092"

    # bootstrap_servers=[‘localhost:9092’] : sets the host and port the producer
    # should contact to bootstrap initial cluster metadata. It is not necessary to set this here,
    # since the default is localhost:9092.
    #
    # value_serializer=lambda x: dumps(x).encode(‘utf-8’): function of how the data
    # should be serialized before sending to the broker. Here, we convert the data to
    # a json file and encode it to utf-8.
    producer = KafkaProducer(bootstrap_servers=[bootstrap_server],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    listener = Listener(producer, config['Resources']['app_topic_name_hashtag'])

    auth = TwitterAuthProvider().getAuth()

    stream = StreamTweets(auth, listener)

    # Converting string to float to get cordinates
    location = [float(x) for x in config['API_param']['location'].split(',')]
    language = config['API_param']['language'].split(' ')
    track_keywords = config['API_param']['track_keywords'].split(' ')
    # track_keywords = "Trump"
    stream.start(location, language, track_keywords)

    # second
    # track_keywords_2 = config['API_param']['track_keywords2'].split(' ')
    # listener2 = Listener(producer, "twitter2")
    # stream2 = StreamTweets(auth, listener2)
    # stream2.start(location, language, track_keywords_2)
