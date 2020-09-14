from kafka import KafkaConsumer
import numpy as np  
import cv2
import config as cfg

# Fire up the Kafka Consumer
topic = cfg.end_topic

consumer = KafkaConsumer(
    topic, 
    bootstrap_servers=['localhost:9092'])

for msg in consumer:
    im_byte = msg.value
    print(im_byte)