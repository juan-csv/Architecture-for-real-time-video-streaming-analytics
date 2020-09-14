# Architecture-for-real-time-video-streaming-analytics
This is an architecture to process video in real time using Kafka as a messaging service and Spark to process frames in real time, the architecture can be summarized in the image below.
![img](https://github.com/juan-csv/Architecture-for-real-time-video-streaming-analytics/blob/master/results/architecture.png)

# Start Zookeeper and kafka
To simplify the tedious task of building a kafka server, we will use Docker with Kafka and Zookeeper out of the box:
Go to the kafka-docker folder
<pre><code>$ cd kafka-docker </code></pre>

Start Kafka and Zookeeper with Docker Compose
<pre><code>$ docker-compose -f docker-compose_local.yml up </code></pre>

In the docker-compose_local.yml configuration file, the topics are defined, the url and the port through which our publisher and subscribers connected.

To stop Kafka uses
<pre><code>$ docker-compose stop </code></pre>
for more information Apache Kafka: Docker Container refer to this [post](https://towardsdatascience.com/kafka-docker-python-408baf0e1088)

# Send frames in real time with Kafka:
We will create a subscriber that takes the webcam frames, transforms them into bytes and sends them to a topic named "distributed-video1"
<pre><code>python my_pub.py </code></pre>

# Get frames in real time with Kafka:
We create a subsriber that pulls the messages we store in the topic "distributed-video1". Spark Streaming is responsible for converting them into a DStream type that can be processed by Spark.
As an example we will take the DStream (RDDs stacked over time), we will extract the frames, we will detect contained faces and we will identify the emotions of the face (check my_sub.py).

<pre><code>python my_sub.py </code></pre>
If you have come this far you should be able to see something like this:
![alt text](https://github.com/juan-csv/Architecture-for-real-time-video-streaming-analytics/blob/master/results/result.gif)

finally we send the result to another kafka topic "final_result_topic" and we consume the result from another subscriber.
<pre><code>python my_sub_end.py </code></pre>

# References
- **kafka-docker:** https://github.com/wurstmeister/kafka-docker/wiki/Connectivity
- **Emotion detection:** https://github.com/juan-csv/emotion_detection

