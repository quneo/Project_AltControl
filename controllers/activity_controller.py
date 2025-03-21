from PyQt6 import QtCore
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.functions import scroll_angle, scroll_param, is_close
from utils.unificate_cords import return_normalized_points


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
            self.process_gesture()
        

    def process_gesture(self):
        """Обработка жеста и генерация действия."""
        action = {}
        animation = {}

        #print(self.current_gesture)
        # 1. Одиночный клик
        if self.current_gesture == 9:
            print("OE")
            action = {'type': 'click', 'button': 'left', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}
            animation = {'type': 'click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 2. Двойной клик
        elif self.current_gesture == 0:
            action = {'type': 'double_click', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}
            animation = {'type': 'double_click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 3. Клик ПКМ
        elif self.current_gesture == 12:
            action = {'type': 'click', 'button': 'right', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}
            animation = {'type': 'right_click', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 4. Зажать ЛКМ
        elif self.current_gesture == 23 and not self.lmb_pressed:
            if is_close(self.current_points_normalized[8], self.current_points_normalized[4]) and not self.lmb_pressed:
                self.lmb_pressed = True
                action = {'type': 'lmb_down', 'button': 'left', 'x': self.current_points[8][0],
                          'y': self.current_points[8][1]}

        # 5. Продолжить выделение
        elif self.current_gesture == 23  and self.lmb_pressed:
            action = {'type': 'follow', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 6. Отпустить ЛКМ
        elif self.current_gesture != 23 and self.prev_gesture == 23 and self.lmb_pressed:
            self.lmb_pressed = False
            action = {'type': 'lmb_up', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 7. Скролл
        elif self.current_gesture == 25 and self.prev_gesture == 25:
            angle = scroll_angle(self.current_points)
            action = {'type': 'scroll', 'scroll_param': scroll_param(angle), 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 8. Свернуть окно
        elif self.current_gesture == 4 and self.prev_gesture == 19:
            action = {'type': 'minimize_window', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 9. Захват окна
        elif self.current_gesture == 19 and self.prev_gesture != 19 and self.window_grabbed == False:
            action = {'type': 'grab_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1], 'dif_x': 0, 'dif_y': 0}
            self.window_grabbed = True

        # 10. Перемещение окна
        elif self.current_gesture == 19 and self.prev_gesture == 19  and self.window_grabbed == True:
            dif_x = int(self.current_points[0][0] - self.prev_points[0][0])
            dif_y = int(self.current_points[0][1] - self.prev_points[0][1])
            action = {'type': 'grab_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1], 'dif_x': dif_x, 'dif_y': dif_y}

        # 11. Отпустить окно
        elif self.current_gesture != 19 and self.window_grabbed == True:
            self.window_grabbed = False

        # 12. Открыть alt-tab
        elif self.current_gesture == 1 and self.alttab == False:
            print("Open")
            action = {'type': 'alt+tab'}
            self.alttab = True

        # 12.5 Закрыть alt-tab
        elif self.current_gesture == 22 and self.alttab == True:
            print("Close")
            action = {'type': 'undo_alt+tab'}
            self.alttab = False

        # 13. Следующее окно
        elif self.current_gesture == 14 and self.alttab and self.prev_gesture != 14:
            """ elif self.current_gesture == 21
            dif_x = int(self.current_points[8][0] - self.prev_points[8][0])
            if dif_x >= 25:
                print("Next")
                action = {'type' : 'next_window'}"
            """
            action = {'type' : 'next_window'}

        # 14. Свернуть все окна
        elif self.current_gesture == 10 and self.alttab == False:
            action = {'type' : 'minimize_all'}


        # Отправка действия на выполнение
        if action:
            self.action_signal.emit(action)
            self.animation_signal.emit(animation)

