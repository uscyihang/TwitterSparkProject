from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import col


bootstrap_server = "localhost:9092"
subscribeType = "subscribe"
input_topic = "twitter"
output_topic = "twitter2"
checkpointLocation = 

if __name__ == "__main__":
    
    # Set up Spark session
    spark = SparkSession \
        .builder \
        .appName("StructuredStreaming") \
        .getOrCreate()

    # Create DataSet representing the stream of input lines from kafka
    lines = spark\
        .readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", bootstrap_server)\
        .option(subscribeType, input_topic)\
        .option("failOnDataLoss", "false")\
        .load()\
        .selectExpr("CAST(value AS STRING)")

    # Split the lines into words
    words = lines.select(
        # explode turns each item in an array into a separate row
        explode(
            split(lines.value, " ")
        ).alias("key")
    )

    # filter words with '#'
    hashtags = words.filter(col("key").startswith("#"))
    
    # count and sort
    hashtagCounts = hashtags.groupBy(col("key")).count().withColumnRenamed("count","value").sort(col("count").desc(), col("key").desc()).limit(10)

    # Start running the query that prints the running counts to the console
    query = hashtagCounts\
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .writeStream\
        .outputMode("complete")\
        .format("kafka")\
        .option("kafka.bootstrap.servers", bootstrap_server)\
        .option("topic", output_topic)\
        .trigger(processingTime="60 seconds")\
        .option("checkpointLocation", checkpointLocation)\
        .start()
    
    query2 = hashtagCounts\
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .writeStream\
        .outputMode("complete")\
        .format("console")\
        .trigger(processingTime="60 seconds")\
        .start()

    query.awaitTermination()
    query2.awaitTermination()