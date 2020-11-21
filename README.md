<!-- PROJECT LOGO -->
<br />
<p align="center">
  <img src="images/logo.png" alt="Logo" width="80" height="80" />
  <h1 align="center">Twitter-Spark-Project</h1>
  <br />
  <p align="center">
    CSCI596 Final Project <br />
    Yihang Wang <br />
    Wei Cheng <br />
    Ruoxuan Wang <br />
  <br />
    <a href="">View Demo</a>
    ·
    <a href="">Report Bug</a>
    ·
    <a href="">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
  * [How it works](#how-it-works)
  * [Architecture](#built-with)
* [Getting Started](#getting-started)
  * [Installation](#installation)
  * [How to run](#how-to-run)
* [Results](#results)
* [Future work](#future-work)
* [Acknowledgements](#acknowledgements)



<!-- ABOUT THE PROJECT -->
## About The Project

In this project, we built a real-time data pipeline using Spark Streaming and Kafka. The basic idea is fetching, analyzing and visualizing realtime twitter data to get the top 10 trending hashtags which contain specific keywords.


### Built With
This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.
* [Tweepy](https://www.tweepy.org/)
* [Apache Kafka](https://kafka.apache.org/)
* [Apache Spark](https://spark.apache.org/) 
* [Node.js](https://nodejs.org/en/)
* [Socket.io](https://socket.io/)
* [HighCharts](https://www.highcharts.com/)

### How it works

* Using Tweepy library to access realtime twitter streaming data through Twitter API, and then send the streams to Kafka.
* Kafka act as the central hub for real-time streams of data, receive streaming data from twitter and persist the data for a specific time period.
* Spark is listening to Kafka topics, waiting for processing those streamings by using complex algorithms such as high-level functions like map, filter, updateStateByKey and countByValues.
* Processed data be pushed out to new Kafka topics.
* Front-end receive data from Kafka topics and visualize the realtime data to interactive charts.


### Architecture

![architecture]




<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Installation

This is an example of how to list things you need to use the software and how to install them.
* Get a free Tweeter developer account and apply for API Keys at [Twitter Developers](https://developer.twitter.com/en)
* [Setup Kafka environment](https://kafka.apache.org/quickstart)
* [Setup Spark environment](https://spark.apache.org/)
* Install Python packages
```sh
pip install -r <dependencies>
```
* Install Npm packages
```sh
npm install <dependencies>
```

### How to run

1. Enter your API keys in `config.conf`
2. Start the Zookeeper Servive
```sh
bin/zookeeper-server-start.sh config/zookeeper.properties
```
3. Start the Kafka broker service
```sh
bin/kafka-server-start.sh config/server.properties
```
4. Create Kafka Topics to store your events
```sh
$ bin/kafka-topics.sh --create --topic <topic_name> --bootstrap-server localhost:9092
```
5. Run `fetch_tweets.py` to fetch data from twitter API
```sh
python fetch_tweets.py 
```
6. Run `analyze_tweets.py` to analyze data by Spark
```sh
python analyze_tweets.py 
```
7. Start npm server
```sh
node dashboard.js
```


<!-- RESULTS -->
## Results

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.
![product-screenshot]


<!-- FUTURE WORK -->
## Future work

 Additional screenshots, code examples and demos work well in this space. You may also link to more resources. Additional screenshots, code examples and demos work well in this space. You may also link to more resources. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Tweepy Documentation](http://docs.tweepy.org/en/latest/index.html)
* [Transformations on DStreams](https://spark.apache.org/docs/latest/streaming-programming-guide.html#transformations-on-dstreams)
* [kafka-python](https://kafka-python.readthedocs.io/en/master/index.html#)
* [Spark Streaming + Kafka Integration Guide](https://spark.apache.org/docs/latest/streaming-kafka-0-10-integration.html)
* [Spark SQL, DataFrames and Datasets Guide](http://spark.apache.org/docs/2.1.0/sql-programming-guide.html)




<!-- MARKDOWN LINKS & IMAGES -->
[logo]: images/logo.png
[architecture]: images/img.png
[product-screenshot]: images/screenshot.png
