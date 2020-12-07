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
        # print(consumer_key)
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth


class Listener(tweepy.StreamListener):

    def __init__(self, kafka_producer, topic_name):
        self.producer = kafka_producer
        self.topic_name = topic_name
        self.count = 0
        self.m_count = 0

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
            if '#' in text:
                self.producer.send(self.topic_name, value={"text": text})
                self.count += 1
                if self.count % 100 == 0:
                    print("Number of tweets with hashtag = ", self.count)

    def collect_mentions(self, raw_data):
        data = json.loads(raw_data)
        if "text" in data:
            text = data["text"]
            if '@' in text:
                self.producer.send(self.topic_name, value={"text": text})
                self.m_count += 1
                if self.m_count % 100 == 0:
                    print("Number of tweets with mentions = ", self.m_count)

    def on_error(self, status_code):
        if status_code == 420:
            print("420 Error!")
            # returning False in on_error disconnects the stream
            return False


class StreamTweets():

    def __init__(self, auth, listener):
        self.stream = tweepy.Stream(auth, listener)

    def start(self, language, track_keywords):
        self.stream.filter(languages=language,
                           track=track_keywords, is_async=True)

    def track_by_location(self, location, language, track_keywords):
        self.stream.filter(languages=language,
                           track=track_keywords, locations=location)


if __name__ == "__main__":

    config = ConfigParser()
    config.read("../conf/config.conf")
    bootstrap_server = config['Kafka_param']['bootstrap.servers']

    producer = KafkaProducer(bootstrap_servers=[bootstrap_server],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    auth = TwitterAuthProvider().getAuth()

    # config search params
    location = [float(x) for x in config['API_param']['location'].split(',')]
    language = config['API_param']['language'].split(' ')
    track_keywords = config['API_param']['track_keywords'].split(' ')

    """
    Hashtag tweets steaming
    """
    hashtag_listener = Listener(producer, config['Resources']['app_topic_name_hashtag'])

    hashtag_stream = StreamTweets(auth, hashtag_listener)

    hashtag_stream.start(language, track_keywords)

    """
    Hashtag tweets steaming
    """
    mention_listener = Listener(producer, config['Resources']['app_topic_name_mention'])

    mention_stream = StreamTweets(auth, mention_listener)

    mention_stream.start(language, track_keywords)

