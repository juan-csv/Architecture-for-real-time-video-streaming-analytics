import config as cfg
import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from keras import backend as K
import tensorflow as tf
import keras

'''
esto es necesario para que no haya errores a la hora de exponer el servicio con flask
info --> https://github.com/tensorflow/tensorflow/issues/28287#issuecomment-495005162
'''
from keras.backend import set_session
sess = tf.Session()
graph = tf.get_default_graph()

set_session(sess)
model_emotions = load_model(cfg.path_model)


class predict_emotions():
    '''
    def __init__(self):
        # cargo modelo de deteccion de emociones
        global graph
        self.graph = tf.get_default_graph()
        self.model_emotions = load_model(cfg.path_model)
    '''

    def preprocess_img(self,face_image,rgb=True,w=48,h=48):
        face_image = cv2.resize(face_image, (w,h))
        if rgb == False:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        face_image = face_image.astype("float") / 255.0
        face_image= img_to_array(face_image)
        face_image = np.expand_dims(face_image, axis=0)
        return face_image

    def get_emotion(self,img,boxes_face):
        emotions = []
        if len(boxes_face)!=0:
            for box in boxes_face:
                y0,x0,y1,x1 = box
                face_image = img[x0:x1,y0:y1]
                # preprocesar data
                face_image = self.preprocess_img(face_image ,cfg.rgb, cfg.w, cfg.h)
                # predecir imagen
                global sess
                global graph
                with graph.as_default():
                    set_session(sess)
                    prediction = model_emotions.predict(face_image)
                    emotion = cfg.labels[prediction.argmax()]
                    emotions.append(emotion)
        else:
            emotions = []
            boxes_face = []
        return boxes_face,emotions

