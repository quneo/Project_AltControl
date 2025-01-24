import time
import pyautogui
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer

from utils.unificate_cords import return_normalized_points, dist, conversion_to_degrees, calculate_absangle


class ActivityController(QtCore.QThread):
    """Промежуточный слой, обрабатывающий входящие жесты. В зависимости от распознанного жеста определяет,
     какое действие необходимо выполнить."""
    action_signal = QtCore.pyqtSignal(dict)  # Передает действие для выполнения

    def __init__(self):
        super().__init__()
        self.current_gesture = None
        self.current_points = None
        self.prev_gesture = None
        self.prev_points = None

    def on_gesture_detected(self, result):
        self.prev_gesture = self.current_gesture
        self.prev_points = self.current_points

        self.current_gesture = result[0]
        self.current_points = result[1]

        self.process_gesture()

    def process_gesture(self):
        """Обработка жеста и генерация действия."""

        action = {}
        if self.current_gesture == 0 and self.prev_gesture == 1:
            action = {'type': 'click', 'button': 'left', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}
            print("Click")

        else:
            pass

        if action:
            self.action_signal.emit(action)

