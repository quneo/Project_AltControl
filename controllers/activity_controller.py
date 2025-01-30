from PyQt6 import QtCore

from utils.functions import scroll_angle, scroll_param, is_close
from utils.unificate_cords import return_normalized_points


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

        self.lmb_pressed = False
        self.window_grabbed = False

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

        # 1. Одиночный клик
        if self.current_gesture == 0 and self.prev_gesture == 1:
            action = {'type': 'click', 'button': 'left', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 2. Двойной клик
        elif self.current_gesture == 2 and self.prev_gesture == 3:
            action = {'type': 'double_click', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 3. Клик ПКМ
        elif self.current_gesture == 7 and self.prev_gesture == 1:
            action = {'type': 'click', 'button': 'right', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 4. Зажать ЛКМ
        elif self.current_gesture == 4 and not self.lmb_pressed:
            if is_close(self.current_points_normalized[8], self.current_points_normalized[4]) and not self.lmb_pressed:
                self.lmb_pressed = True
                action = {'type': 'lmb_down', 'button': 'left', 'x': self.current_points[8][0],
                          'y': self.current_points[8][1]}

        # 5. Продолжить выделение
        elif self.current_gesture == 4 and self.prev_gesture == 4 and self.lmb_pressed:
            action = {'type': 'follow', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 6. Отпустить ЛКМ
        elif self.current_gesture != 4 and self.prev_gesture == 4 and self.lmb_pressed:
            self.lmb_pressed = False
            action = {'type': 'lmb_up', 'button': 'left', 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 7. Скролл
        elif self.current_gesture == 13 and self.prev_gesture == 13:
            angle = scroll_angle(self.current_points)
            action = {'type': 'scroll', 'scroll_param': scroll_param(angle), 'x': self.current_points[8][0],
                      'y': self.current_points[8][1]}

        # 8. Закрыть окно
        elif self.current_gesture == 6 and self.prev_gesture == 5:
            action = {'type': 'close_window', 'x': self.current_points[8][0], 'y': self.current_points[8][1]}

        # 9. Захват окна
        elif self.current_gesture == 5 and self.prev_gesture != 5 and self.window_grabbed == False:
            action = {'type': 'grab_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1], 'dif_x': 0, 'dif_y': 0}
            print('52')
            self.window_grabbed = True

        # 10. Перемещение окна
        elif self.current_gesture == 5 and self.prev_gesture == 5 and self.window_grabbed == True:
            dif_x = int(self.current_points[0][0] - self.prev_points[0][0])
            dif_y = int(self.current_points[0][1] - self.prev_points[0][1])
            action = {'type': 'grab_window', 'x': self.current_points[0][0], 'y': self.current_points[0][1], 'dif_x': dif_x, 'dif_y': dif_y}

        # 11. Отпустить окно
        elif self.current_gesture != 5 and self.window_grabbed == True:
            self.window_grabbed = False


        # Отправка действия на выполнение
        if action:
            self.action_signal.emit(action)

