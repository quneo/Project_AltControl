import numpy as np
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QRect, QThread, pyqtSignal
import cv2 as cv

from models.models import *
from utils.functions import fingers_bias
from utils.unificate_cords import classification


class GestureRecognizer(QThread):
    gesture_signal = pyqtSignal(tuple)

    def __init__(self, screen_width, screen_height, model_quality, camera_id):
        super().__init__()
        self.width, self.height = screen_width, screen_height
        self.camera_id = camera_id

        # Инициализация камеры
        self.capture = cv.VideoCapture(self.camera_id, cv.CAP_DSHOW)
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, self.width)  # Ширина кадров в видеопотоке.
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)  # Высота кадров в видеопотоке

        self.localizer_hands = localizer_model()
        self.classificator = self._initialize_classificator(model_quality)

    @staticmethod
    def _initialize_classificator(model_quality):
        """Инициализирует классификатор в зависимости от качества модели."""
        if model_quality == 0:
            return tiny_model()
        elif model_quality == 1:
            return amazing_model()
        else:
            raise ValueError(f"Некорректное значение model_quality: {model_quality}")

    def recogniseGesture(self, points):
        """Распознает жест на основе ключевых точек."""
        result = classification(points, self.classificator)
        cur_gesture, confidence = np.argmax(result), round(np.max(result), 4)  # Результат классификации
        if confidence <= 0.6:
            cur_gesture = 15  # Неопределенный жест, если уверенность низкая
        return cur_gesture, confidence

    def process_frame(self, frame):
        """Обрабатывает один кадр для извлечения жестов и ключевых точек."""
        frame = cv.flip(frame, 1)  # Отразить изображение горизонтально
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # Преобразовать в RGB
        result = self.localizer_hands.process(frame)  # Обработка изображения моделью

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                # Извлечение ключевых точек
                points = np.array([
                    (int(hand.landmark[i].x * self.width), int(hand.landmark[i].y * self.height))
                    for i in range(21)
                ])

                # Распознавание жеста
                gesture, confidence = self.recogniseGesture(points)

                # Применение коррекции
                points = fingers_bias(points)

                # Передача жеста и точек через сигнал
                self.gesture_signal.emit((gesture, points))
        else:
            # Передача сигнала для неопределенного жеста
            self.gesture_signal.emit((15, None))

    def run(self):
        """Основной цикл для захвата и обработки кадров."""
        while True:
            ret, frame = self.capture.read()
            if ret:
                self.process_frame(frame)