import mediapipe as mp
import numpy as np
import tensorflow as tf
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.unificate_cords import *
from models import *
from collections import deque


def compute_threshold(value, alpha=0.06, beta=0.04, g=1.3): 
    threshold = (1-g)*value + g*alpha

    if threshold >= alpha:
        return alpha 
    elif threshold <= beta:
        return beta
    else:
        return threshold

def threshold_boost(x, threshold=0.1, boost_factor=2):
    if x > threshold:
        boosted_x = x * boost_factor
        if boosted_x <= 1:
            return boosted_x
        else:
            return 1
    return x


class GestureEnergyAnalyzer:
    def __init__(self, window_size=3, min_frame_gap=4, adaptive_threshold_window=15, confirm_window=5, history_len=200, keep_last=20):
        """
        Класс, анализирующий энергию движения руки для выделения временных рамок выполнения жеста.

        param: window_size - Размер скользящего дня для сглаживания энергии.
        param: min_frame_gap - Минимальное расстояние между выделенными моментами.
        param: adaptive_threshold_window - Размер окна, на основании которого расчитывается адаптивный порог.
        param: confirm_window - Размер окна подтверждения.
        param: history_len - Длина хранимой истории.
        param: selected_indices - индексы, по которым вычисляется средняя точка руки.
        """

        # Параметры алгоритма
        self.window_size = window_size  
        self.min_frame_gap = min_frame_gap
        self.adaptive_threshold_window = adaptive_threshold_window
        self.confirm_window = confirm_window
        self.history_len = history_len
        self.keep_last = keep_last
        self.selected_indices = [0, 4, 8, 12, 16, 20]

        # История данных
        self.energy_history = deque(maxlen=self.history_len)  # Запоминаем последние 100 значений
        self.smoothed_history = deque(maxlen=self.history_len)
        self.threshold_history = deque(maxlen=self.history_len)
        self.event_frames = deque(maxlen=self.history_len) 

        self.landmarks_history = []

        # Счетчики и состояния
        self.under_threshold_counter = 0
        self.current_frame = 0
        self.prev_landmarks = None
        self.prev_angles = None

    def process_motion(self, landmarks):
        self.landmarks_history.append(landmarks)
        self.compute_energy(landmarks)
        self._smooth_energy()
        self._compute_threshold()
        seq = self._check_event()
        self._reset()
        
        return seq
    
    def compute_energy(self, landmarks):
        if landmarks.shape != (21, 2):
            raise ValueError(f"Wrong landmarks shape")  # Проверяем размер поданных точек
        
        norm_landm = return_normalized_points(np.array(landmarks))  # Нормализуем координаты
        if self.prev_landmarks is not None:
            center_cur = np.mean(norm_landm[self.selected_indices], axis=0)    # Вычисляем среднюю точку
            center_prev = np.mean(self.prev_landmarks[self.selected_indices], axis=0)
            delta = center_cur - center_prev    # Вычисляем расстояние между точками
            energy = threshold_boost(np.linalg.norm(delta))    # Вычисляем энергию
            self.energy_history.append(energy)     # Добавляем вычисленное значение энергии в список

        self.prev_landmarks = norm_landm    # Сохраняем текущие точки 

    def gesture_character(self, seq_len):
        """
        Проверяем, статический ли жест:
        False - динамичный
        True - статичный
        """
        if len(self.smoothed_history) < seq_len:
            return True  # Недостаточно данных, считаем динамическим

        # Проверяем условие для последних seq_len значений
        return all(sm < th for sm, th in zip(
            list(self.smoothed_history)[-seq_len:],
            list(self.threshold_history)[-seq_len:]
        ))

    def _smooth_energy(self):
        if len(self.energy_history) >= self.window_size:
            smoothed_value = np.mean(list(self.energy_history)[-self.window_size:])
        else:
            smoothed_value = np.nan  # Если недостаточно значений, ставим NaN

        self.smoothed_history.append(smoothed_value)

    def _compute_threshold(self):
        if len(self.energy_history) >= self.adaptive_threshold_window:
            threshold_value = compute_threshold(np.mean(list(self.energy_history)[-self.adaptive_threshold_window:]))
        else:
            threshold_value = np.nan  # Если недостаточно значений, ставим NaN
        self.threshold_history.append(threshold_value)

    def _check_event(self):
        # Добавление момента события
        if len(self.smoothed_history) == 0 or len(self.threshold_history) == 0:
            return
        
        smoothed_value = self.smoothed_history[-1]
        threshold_value = self.threshold_history[-1]
        current_frame = len(self.energy_history) - 1

        if not np.isnan(smoothed_value) and not np.isnan(threshold_value):
            if smoothed_value <= threshold_value:
                self.under_threshold_counter += 1
                if self.under_threshold_counter >= self.confirm_window:
                    if len(self.event_frames) == 0 or (current_frame - self.event_frames[-1] >= self.min_frame_gap):
                        self.event_frames.append(current_frame)
                        self.under_threshold_counter = 0
                        seq = list(self.landmarks_history)
                        self.landmarks_history.clear()
                        return seq
            else:
                self.under_threshold_counter = 0

        return None

    def _reset(self):
        if len(self.energy_history) >= self.history_len:
            # Сохраняем последние `keep_last` значений
            last_energy = list(self.energy_history)[-self.keep_last:]
            last_smoothed = list(self.smoothed_history)[-self.keep_last:]
            last_threshold = list(self.threshold_history)[-self.keep_last:]

            # Сбрасываем очереди
            self.energy_history = deque(last_energy, maxlen=self.history_len)
            self.smoothed_history = deque(last_smoothed, maxlen=self.history_len)
            self.threshold_history = deque(last_threshold, maxlen=self.history_len)
            self.event_frames = deque(maxlen=self.history_len) 

            self.landmarks_history = []