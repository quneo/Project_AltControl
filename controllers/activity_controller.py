import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Добавляет текущую папку
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath("C:/Users/vadin/Git/Project_AltControl/Project_AltControl/gestures"))
from PyQt6 import QtCore
from utils.functions import scroll_angle, scroll_param, is_close
from utils.unificate_cords import return_normalized_points

from gestures.gesture_list import *

class ActivityController(QtCore.QThread):
    """Промежуточный слой, обрабатывающий входящие жесты. В зависимости от распознанного жеста определяет,
     какое действие необходимо выполнить."""
    action_signal = QtCore.pyqtSignal(dict)  # Передает действие для выполнения
    animation_signal = QtCore.pyqtSignal(dict)  # Передает анимацию для отображения

    def __init__(self):
        super().__init__()
        self.current_gesture = None
        self.current_points = None
        self.prev_gesture = None
        self.prev_points = None

        self.lmb_pressed = False
        self.window_grabbed = False
        self.alttab = False

    def on_gesture_detected(self, result):
        self.prev_gesture = self.current_gesture
        self.prev_points = self.current_points

        self.current_gesture = result[0]
        self.current_points = result[1]
        if self.current_points is not None:
            self.current_points_normalized = return_normalized_points(self.current_points)
            if self.current_gesture != None and self.prev_gesture != None:
                self.process_gesture()
        

    def process_gesture(self):
        """Обработка жеста и генерация действия."""
        action = {}
        animation = {}

        # 1. Одиночный клик
        if inverse_class_map[self.current_gesture] == 'd_lbm+':
            action = {'type': 'click', 'button': 'left', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}
            animation = {'type': 'click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 2. Двойной клик
        elif inverse_class_map[self.current_gesture] == 'd_2lbm+':
            action = {'type': 'double_click', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}
            animation = {'type': 'double_click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 3. Клик ПКМ
        elif inverse_class_map[self.current_gesture] == 'd_rbm+':
            action = {'type': 'click', 'button': 'right', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}
            animation = {'type': 'right_click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 4. Зажать ЛКМ
        elif inverse_class_map[self.current_gesture] == 's_ok' and not self.lmb_pressed:
            if is_close(self.current_points_normalized[8], self.current_points_normalized[4]) and not self.lmb_pressed:
                self.lmb_pressed = True
                action = {'type': 'lmb_down', 'button': 'left', 'x': self.current_points[8][0],
                          'y': self.current_points[8][1]}

        # 5. Продолжить выделение
        elif inverse_class_map[self.current_gesture] == 's_ok'  and self.lmb_pressed:
            action = {'type': 'follow', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 6. Отпустить ЛКМ
        elif inverse_class_map[self.current_gesture] != 's_ok' and inverse_class_map[self.prev_gesture] == 's_ok' and self.lmb_pressed:
            self.lmb_pressed = False
            action = {'type': 'lmb_up', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 7. Скролл
        elif inverse_class_map[self.current_gesture] == 's_pinch' and inverse_class_map[self.prev_gesture] == 's_pinch':
            angle = scroll_angle(self.current_points)
            action = {'type': 'scroll', 'scroll_param': scroll_param(angle), 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 9. Захват окна
        elif inverse_class_map[self.current_gesture] == 'd_palm_2_fist' and self.window_grabbed == False:
            action = {'type': 'grab_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1]}
            self.window_grabbed = True

        # 10. Перемещение окна
        elif inverse_class_map[self.current_gesture] == 's_fist' and self.window_grabbed == True:
            dif_x = int(self.current_points[0][0] - self.prev_points[0][0])
            dif_y = int(self.current_points[0][1] - self.prev_points[0][1])
            action = {'type': 'move_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1], 'dif_x': dif_x, 'dif_y': dif_y}

        # 11. Отпустить окно
        elif inverse_class_map[self.current_gesture] == 'd_fist_2_palm' and self.window_grabbed == True:
            action = {'type': 'release_window'}
            self.window_grabbed = False

        # 8. Свернуть окно
        elif inverse_class_map[self.current_gesture] == 'd_fist_down' and self.window_grabbed == True:
            action = {'type': 'minimize_window'}
            self.window_grabbed = False

        # 12. Открыть alt-tab
        elif inverse_class_map[self.current_gesture] == 'd_attract' and self.alttab == False:
            action = {'type': 'alt+tab'}
            self.alttab = True

        # 12.5 Закрыть alt-tab
        elif inverse_class_map[self.current_gesture] == 's_like' and self.alttab == True:
            action = {'type': 'undo_alt+tab'}
            self.alttab = False

        # 13. Следующее окно
        elif inverse_class_map[self.current_gesture] == 'd_right_swing' and self.alttab and inverse_class_map[self.prev_gesture] != 'd_right_swing':
            action = {'type' : 'next_window'}

        # 14. Свернуть все окна
        elif inverse_class_map[self.current_gesture] == 'd_left_swing' and self.alttab == False:
            action = {'type' : 'minimize_all'}

        # 15. Скриншот 
        elif inverse_class_map[self.current_gesture] == 'd_carousel':
            action = {'type': 'take_screenshot'}

        elif inverse_class_map[self.current_gesture] == 'd_gun_up':
            action = {'type': 'paste'}

        elif inverse_class_map[self.current_gesture] == 'd_gun_down':
            action = {'type': 'copy'}

        # Отправка действия на выполнение
        if action:
            self.action_signal.emit(action)
            self.animation_signal.emit(animation)

