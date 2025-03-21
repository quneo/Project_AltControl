import mediapipe as mp
import tensorflow as tf
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.unificate_cords  import *
from utils.functions import *
from gesture_list import *

class SequenceClassifier:
    def __init__(self, model_static, model_dynamic,  SEQ_LEN=100, threshold=0.6):
        self.dynamic_class_map = inverse_dynamic_class_map
        self.static_class_map = inverse_static_class_map
        self.model_static = model_static
        self.model_dynamic = model_dynamic
        self.SEQ_LEN = SEQ_LEN
        self.threshold = threshold

    def classify(self,character, seq):
        if character == False:
            input = self.dynamic_process(seq)
            prediction = self.get_prediction_dynamic(input)
            return prediction
    
        elif character == True:
            input = self.static_process(seq)
            prediction = self.get_prediction_static(input)
            return prediction

    def get_prediction_dynamic(self, seq):
        pred = self.model_dynamic.predict(seq, verbose=0)[0]
        predicted_label = np.argmax(pred, axis=-1)
        confidence = pred[predicted_label]

        if confidence > self.threshold:
            gesture_name = inverse_dynamic_class_map[predicted_label]  # Получаем имя жеста
            return class_map[gesture_name], confidence  # Возвращаем индекс из class_map
        return None, confidence
        
    def get_prediction_static(self, seq):
        pred = self.model_static.predict(seq, verbose=0)[0]
        predicted_label = np.argmax(pred, axis=-1)
        confidence = pred[predicted_label]

        if confidence > self.threshold:
            gesture_name = inverse_static_class_map[predicted_label]  # Получаем имя жеста
            return class_map[gesture_name], confidence  # Возвращаем индекс из class_map
        return None, confidence

    def static_process(self, seq):
        seq = np.array(seq).reshape(-1, 21, 2)
        seq = seq[-1:]
        seq = np.array([unificate_hand2(x) for x in seq])
        seq = seq.reshape(-1, 21, 2)
        seq = np.array([return_normalized_points(x) for x in seq])
        model_input = np.expand_dims(seq, axis=0)
        return model_input

    def dynamic_process(self, seq):
        seq = np.array(seq).reshape(-1, 21, 2)

        # 1. Вычисляем bbox (до нормализации keypoints)
        bbox_seq = np.array([get_bbox(frame) for frame in seq])  # (LEN, 2, 2)
        bbox_seq = bbox_seq.reshape(-1, 4)  # Приводим к (LEN, 4)

        # 2. Нормируем bbox 
        bbox_seq[:, [0, 2]] /= 1280  # x_min и x_max
        bbox_seq[:, [1, 3]] /= 720  # y_min и y_max

        # 3. Вычисляем угол
        angles_seq = np.array([calculate_absangle(frame) for frame in seq])  # (LEN,)
        angles_seq = angles_seq.reshape(-1, 1)  # Приводим к (LEN, 1)

        seq = np.array([return_normalized_points(x) for x in seq])

        seq = np.concatenate([seq.reshape(-1, 42), bbox_seq, angles_seq], axis=-1)  # (LEN, 47)

        seq = np.pad(seq, ((0, self.SEQ_LEN - seq.shape[0]), (0, 0)), mode='constant', constant_values=0)

        model_input = np.expand_dims(seq, axis=0)
        
        return model_input
    


