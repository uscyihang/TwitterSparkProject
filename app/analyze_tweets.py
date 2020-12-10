from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import Row, SQLContext
import json
import sys
from os import environ
from kafka import KafkaProducer
from configparser import ConfigParser


def set_global_topic_name(config):
    globals()['dashboard_topic_name'] = config['Resources']['dashboard_topic_name']
    globals()['dashboard_topic_name_mention'] = config['Resources']['dashboard_topic_name_mention']


def sum_all_tags(new_values, last_sum):
    if last_sum is None:
        return sum(new_values)
    return sum(new_values) + last_sum


def getSparkSessionInstance(spark_context):
    if ('sparkSessionSingletonInstance' not in globals()):
        globals()['sparkSessionSingletonInstance'] = SQLContext(spark_context)
    return globals()['sparkSessionSingletonInstance']


def process_tweets(rdd, producer):
    try:
        spark_sql = getSparkSessionInstance(rdd.context)

        rowRdd = rdd.map(lambda tag: Row(hashtag=tag[0], frequency=tag[1]))

        hashtagsDataFrame = spark_sql.createDataFrame(rowRdd)

        hashtagsDataFrame.createOrReplaceTempView("tweets_text")

        hashtagCountsDataFrame = spark_sql.sql(
            "select hashtag, frequency from tweets_text order by frequency desc limit 10")

        send_to_kafka(hashtagCountsDataFrame, producer)

    except:
        e = sys.exc_info()[0]
        print(e)


def send_to_kafka(hashtagCountsDataFrame, producer):

    top_rows = dict()

    for data, frequency in hashtagCountsDataFrame.collect():
        top_rows[data] = frequency

    producer.send(globals()['dashboard_topic_name'], value=top_rows)


def define_kafka_param(config):
    kafkaParam = {
        "zookeeper.connect": config['Kafka_param']['zookeeper.connect'],
        "group.id": config['Kafka_param']['group.id'],
        "zookeeper.connection.timeout.ms": config['Kafka_param']['zookeeper.connection.timeout.ms'],
        "bootstrap.servers": config['Kafka_param']['bootstrap.servers']
    }

    return kafkaParam


def create_tweets_dstream(ssc, input_msg, kafka_param, mark):
    tweets_stream = KafkaUtils.createDirectStream(
        ssc, input_msg, kafkaParams=kafka_param,
        valueDecoder=lambda x: json.loads(x.decode('utf-8')))

    return tweets_stream.map(lambda v: v[1]["text"]) \
        .flatMap(lambda t: t.split(" ")) \
        .filter(lambda tag: len(tag) > 2 and mark == tag[0]) \
        .countByValue() \
        .updateStateByKey(sum_all_tags)


def start():
    config = ConfigParser()

    config.read("conf/config.conf")

    set_global_topic_name(config)

    pyspark_environ = config['Resources']['pyspark_environ']

    environ['PYSPARK_SUBMIT_ARGS'] = pyspark_environ

    sparkConf = SparkConf("TwitterSparkProject")

    sparkConf.setMaster("local[*]")

    sc = SparkContext(conf=sparkConf)

    sc.setLogLevel("INFO")

    ssc = StreamingContext(sc, 10)

    ssc.checkpoint("checkpointTwitterApp")

    kafka_param = define_kafka_param(config)

    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    """
    HashTag DStream for getting input from Kafka and process.
    """
    create_tweets_dstream(ssc, [config['Resources']['app_topic_name_hashtag']], kafka_param, "#")\
        .foreachRDD(lambda x: process_tweets(x, producer))
    """
    Mention DStream for getting input from Kafka and process.
    """
    create_tweets_dstream(ssc, [config['Resources']['app_topic_name_mention']], kafka_param, "@")\
        .foreachRDD(lambda x: process_tweets(x, producer))

    # Start Streaming Context
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    start()
