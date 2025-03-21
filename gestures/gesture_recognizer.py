import numpy as np
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QRect, QThread, pyqtSignal
import cv2 as cv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.models import *
from utils.functions import fingers_bias
from utils.unificate_cords import classification
from settings import *

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from SequenceClassifier import SequenceClassifier
from GestureEnergyAnalyzer import GestureEnergyAnalyzer


class GestureRecognizer(QThread):
    gesture_signal = pyqtSignal(tuple)
    get_activity_signal = pyqtSignal(tuple)

    def __init__(self, screen_width, screen_height, model_quality, camera_id):
        super().__init__()
        self.width, self.height = screen_width, screen_height
        self.camera_id = camera_id

        # Инициализация камеры
        self.capture = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.width)  # Ширина кадров в видеопотоке.
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)  # Высота кадров в видеопотоке

        self.localizer_hands = localizer_model()
        self.classificator = self._initialize_classificator()
        self.energy_analyzer = self._initialize_analyzer()

        self.history = []

    @staticmethod
    def _initialize_classificator():
        """Инициализирует классификатор."""

        classificator = SequenceClassifier(
            model_static=static_gesture_model(),
            model_dynamic=dynamic_gesture_model() 
        )

        return classificator
    
    @staticmethod
    def _initialize_analyzer():
        # Параметры
        history_len = 200
        window_size = 3
        min_frame_gap = 4
        adaptive_threshold_window = 10
        confirm_window = 2

        # Инициализация вашего класса
        analyzer = GestureEnergyAnalyzer(
            window_size=window_size,
            min_frame_gap=min_frame_gap,
            adaptive_threshold_window=adaptive_threshold_window,
            confirm_window=confirm_window,
            history_len=history_len,
            keep_last=20  # Сохраняем последние 20 значений при сбросе
        )

        return analyzer

    def moving_average(self, points):
        self.history.append(points)
        length = len(self.history)
        if length > MAW:
            self.history = self.history[-MAW:]

        av_points = sum(self.history) / length
        return av_points.astype(int)
    

    def process_frame(self, frame):
        """Обрабатывает один кадр для извлечения жестов и ключевых точек."""
        frame = cv.flip(frame, 1)  # Отразить изображение горизонтально
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # Преобразовать в RGB
        result = self.localizer_hands.process(frame)  # Обработка изображения моделью

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                gesture, confidence = None, 0
                # Извлечение ключевых точек
                points = np.array([
                    (int(hand.landmark[i].x * self.width), int(hand.landmark[i].y * self.height))
                    for i in range(21)
                ])

                seq = self.energy_analyzer.process_motion(points)

                # Применение коррекции
                points = fingers_bias(points)

                # Применение скользящего среднего
                points_prepared = self.moving_average(points)
                
                if seq is not None:
                    character = self.energy_analyzer.gesture_character(len(seq))
                    gesture, confidence = self.classificator.classify(character, seq)
                    self.get_activity_signal.emit((gesture, points_prepared))

                # Передача жеста и точек через сигнал
                self.gesture_signal.emit((gesture, points_prepared))
        else:
            # Передача сигнала для неопределенного жеста
            self.gesture_signal.emit((26, None))
            

    def run(self):
        """Основной цикл для захвата и обработки кадров."""
        while True:
            ret, frame = self.capture.read()
            if ret:
                self.process_frame(frame)