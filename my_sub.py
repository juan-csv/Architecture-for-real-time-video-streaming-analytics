import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--jars /Users/macbook/opt/anaconda3/lib/python3.7/site-packages/pyspark/jars/spark-streaming-kafka-0-8-assembly_2.11-2.4.6.jar pyspark-shell'
import cv2
import json
import numpy as np
import config as cfg
from pyspark.streaming.kafka import KafkaUtils
from pyspark.streaming import StreamingContext
from pyspark import SparkContext, SparkConf
import pyspark
import dlib
from emotion_detection import f_emotion_detection


#------------------------------------------------------------------------------------------------------------------------------------------
#                                               obtener frames del mensaje
def deserializer(im_byte):
    # bytes --> jpg
    decoByte = np.frombuffer(im_byte, dtype=np.uint8)
    # Jpg --> unit8
    decoJpg = cv2.imdecode(decoByte, cv2.IMREAD_COLOR)
    return decoJpg
#------------------------------------------------------------------------------------------------------------------------------------------
#                                           Obtener bounding box rostros
def get_faces(m):
    im = m[1]
    try:
        gray =  cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        rectangles = frontal_face_detector(gray, 0)
        boxes_face = convert_rectangles2array(rectangles,im)
        return (im,boxes_face)
    except:
        return im


def convert_rectangles2array(rectangles,image):
    res = np.array([])
    for box in rectangles:
        [x0,y0,x1,y1] = max(0, box.left()), max(0, box.top()), min(box.right(), image.shape[1]), min(box.bottom(), image.shape[0])
        new_box = np.array([x0,y0,x1,y1])
        if res.size == 0:
            res = np.expand_dims(new_box,axis=0)
        else:
            res = np.vstack((res,new_box))
    return res

#------------------------------------------------------------------------------------------------------------------------------------------
#                                           Obtener emociones
def get_emotions(m):
    try: 
        im = m[0]
        boxes_face = m[1]
        _,emotion  = emotion_detector.get_emotion(im,boxes_face)
        return emotion
    except:
        return "error in get_emptions"
#------------------------------------------------------------------------------------------------------------------------------------------
#                                               Enviar el resultado a un topic   
from kafka import KafkaProducer
my_producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def message_sender(m):
    """Send (key, value) to a Kafka producer"""
    my_producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    my_producer.send(cfg.end_topic,m)
    return m

# ------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # instancio detectores
    frontal_face_detector   = dlib.get_frontal_face_detector()
    emotion_detector        = f_emotion_detection.predict_emotions()

    # creo contextos de spark y spark_streaming
    conf = SparkConf()
    # instancio mi conexto de spark en local y le doy un nombre a mi job
    sc = SparkContext(master="local", appName='video_streaming_job', conf=conf)
    sc.setLogLevel('WARN')

    # instancio mi contexto de streaming y defino la duracion de cada batch a analizar
    n_secs = 0.5  # en segundos
    ssc = StreamingContext(sparkContext=sc, batchDuration=n_secs)

    kafkaParams = {'bootstrap.servers':'localhost:9092', 
                    'fetch.message.max.bytes':'15728640',
                    'auto.offset.reset':'largest'}
    stream = KafkaUtils.createDirectStream(ssc=ssc,
                    topics=[cfg.topic],
                    kafkaParams=kafkaParams,
                    valueDecoder=lambda v: deserializer(v))  
    
    # inicio pipeline                                     
    stream.map(
            get_faces
        ).map(
            get_emotions
        ).map(
            message_sender
        ).pprint()

    # comienza la computación de streaming
    ssc.start()
    # espera que la transmisión termine
    ssc.awaitTermination()