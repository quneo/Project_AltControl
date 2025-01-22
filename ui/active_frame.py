import numpy as np
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QRect

from colors import Frame_color, Hand_landmark_color
from utils.constants import connections
from utils.functions import bbox_cords
from gestures import gesture_list


class ActiveFrame(QMainWindow):
    def __init__(self, camera_index, model_quality, frame_show, bbox_show):
        super().__init__()
        self.pen_frame = QPen(QColor(0, Frame_color, 0, 200))
        self.bbox_show = bbox_show
        self.frame_show = frame_show
        self.model_quality = model_quality
        self.camera_index = camera_index
        self.finger_points = None
        self.cur_gesture = None
        self.Frame_color = Frame_color

        self.setup_window()
        self.init_pens_and_brushes()

    def setup_window(self):
        """Настройка внешнего вида окна."""
        self.setWindowTitle("Project AltControl")
        screen = QApplication.primaryScreen().geometry()  # Получаем размер экрана через QScreen
        self.WIDTH, self.HEIGHT = screen.width(), screen.height()
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        # Устанавливаем прозрачный фон и безрамочный режим
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

    def init_pens_and_brushes(self):
        """Инициализация кистей и пера, которые будут использоваться в отрисовке."""
        # Перо для рамки
        pen_width = int(np.log(self.Frame_color) * np.sin(self.Frame_color / 15) ** 2 + self.Frame_color / 50)
        self.pen_frame.setWidth(pen_width)

        # Перо для ключевых точек руки
        self.pen_landmarks = QPen(QColor(0, Hand_landmark_color, 0))
        self.pen_landmarks.setWidth(3)

        # Кисть для заливки эллипсов (прозрачный цвет)
        self.brush_landmarks = QColor(0, 200, 0)  # Полупрозрачный зеленый

        # Перо для линий между точками
        self.pen_lines = QPen(QColor(0, 200, 0))  # Зеленое с прозрачностью
        self.pen_lines.setWidth(4)

    def draw_frame(self, painter):
        """Рисует прямоугольную рамку на экране с плавной настройкой цвета и толщины линии."""
        painter.setPen(self.pen_frame)
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRect(QRect(3, 3, self.WIDTH - 5, self.HEIGHT - 50))

    def draw_hand_landmarks(self, painter, points):
        """Отрисовка ключевых точек руки и линий соединений между ними."""
        painter.setPen(self.pen_landmarks)
        painter.setBrush(self.brush_landmarks)

        for point in points:
            painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)  # Радиус эллипсов = 7

        painter.setPen(self.pen_lines)
        # Рисуем линии между точками (если есть соединения)
        for connection in connections:
            painter.drawLine(
                QPoint(self.finger_points[connection[0]][0], self.finger_points[connection[0]][1]),
                QPoint(self.finger_points[connection[1]][0], self.finger_points[connection[1]][1])
            )

    def draw_bbox(self, painter, points):
        painter.setPen(self.pen_landmarks)
        painter.setBrush(self.brush_landmarks)
        """Отрисовка ограничивающей рамки вокруг руки."""
        bbox = bbox_cords(self.finger_points)
        text = gesture_list[self.cur_gesture]  # Текст, который нужно отобразить
        font = painter.font()  # Получаем текущий шрифт
        font.setPointSize(20)  # Устанавливаем размер шрифта
        painter.setFont(font)  # Применяем шрифт к painter
        painter.drawText(QPoint(bbox[0], bbox[1] - 10), text)

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.bbox_show:
            self.draw_frame(painter)

        if self.finger_points is not None:
            self.draw_hand_landmarks(painter, self.finger_points)
            if self.bbox_show:
                self.draw_bbox(painter, self.finger_points)
            if self.Frame_color <= 200:
                self.Frame_color += 1

        else:
            if self.Frame_color >= 50:
                self.Frame_color -= 1

        painter.end()


class ActiveFrame1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.finger_points = None
        self.cur_gesture = None
        self.setWindowTitle("Project AltControl")

        self.is_active = 0

        # Получаем размер экрана через QScreen
        screen = QApplication.primaryScreen().geometry()
        self.WIDTH, self.HEIGHT = screen.width(), screen.height()
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        # Устанавливаем прозрачный фон и безрамочный режим
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowDoesNotAcceptFocus, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.selected_window = None

        self.Frame_color = 50

        self.camera_id = 0

        self.frame_show = True

        self.show_bbox = True

        # Создаем потоки
        self.gesture_thread1 = GestureRecognizer(screen.width(), screen.height())
        self.gesture_thread1.gesture_signal.connect(self.on_gesture_detected)
        self.gesture_thread1.start()

        self.cursor_controller = CursorController()
        self.cursor_controller.start()

        self.mouse_thread = MouseController(self.cursor_controller)
        self.mouse_thread.gesture_signal.connect(self.cursor_controller.update_gesture)
        self.mouse_thread.control_window_signal.connect(self.control_window)
        self.mouse_thread.scrolling_signal.connect(self.cursor_controller.perform_scroll)
        self.mouse_thread.window_moving_signal.connect(self.move_window)
        self.gesture_thread1.gesture_signal.connect(self.mouse_thread.handle_gesture)
        self.mouse_thread.start()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_tracking)  # Перерисовываем каждые 20 мс
        self.update_timer.start(20)

    def update_active_flag(self, flag):
        self.is_active = flag

    def update_tracking(self):
        if self.is_active == 1:
            self.update()

    def hide_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def close_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def restore_window(self):
        if self.selected_window is not None:
            self.selected_window.minimize()

    def move_window(self, point):
        if self.selected_window is not None:
            self.cursor_controller.move_window(self.selected_window, point)

    def control_window(self, action):
        if action == 0:
            self.hide_window()
        elif action == 1:
            self.close_window()
        elif action == 2:
            self.restore_window()

    def on_gesture_detected(self, result):
        self.finger_points = result[1]
        self.cur_gesture = result[0]
        if self.finger_points is not None:
            try:
                self.selected_window = gw.getWindowsAt(self.finger_points[8][0], self.finger_points[8][1])[1]
            except:
                self.selected_window = None
        else:
            self.selected_window = None

    def paintEvent(self, event):

        painter = QPainter(self)

        # Настраиваем перо и кисть для эллипсов
        pen_ellipses = QPen(QColor(0, 200, 0))  # Цвет с прозрачностью (альфа = 200)
        pen_ellipses.setWidth(3)  # Толщина линий для эллипсов
        painter.setPen(pen_ellipses)

        # Кисть для заливки эллипсов (прозрачная заливка)
        brush_ellipses = QColor(0, 200, 0)  # Полупрозрачный синий
        painter.setBrush(brush_ellipses)
        if self.finger_points is not None:
            # Рисуем эллипсы для всех точек
            for point in self.finger_points:
                painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)  # Радиус эллипсов = 5

            # Настраиваем перо для линий (соединений)
            pen_lines = QPen(QColor(0, 200, 0))  # Зеленый с прозрачностью (альфа = 150)
            pen_lines.setWidth(4)  # Толщина линий для соединений
            painter.setPen(pen_lines)

            # Рисуем соединения
            for connection in connections:
                painter.drawLine(QPoint(self.finger_points[connection[0]][0], self.finger_points[connection[0]][1]),
                                 QPoint(self.finger_points[connection[1]][0], self.finger_points[connection[1]][1]))

            if self.show_bbox == True:
                painter.setPen(QColor(0, 170, 0))
                painter.setBrush(Qt.GlobalColor.transparent)

                bbox = bbox_cords(self.finger_points)
                painter.drawRect(QRect(bbox[0], bbox[1], bbox[2], bbox[3]))
                text = gestures[self.cur_gesture]  # Текст, который нужно отобразить
                font = painter.font()  # Получаем текущий шрифт
                font.setPointSize(20)  # Устанавливаем размер шрифта
                painter.setFont(font)  # Применяем шрифт к painter
                painter.drawText(QPoint(bbox[0], bbox[1] - 10), text)

            if self.Frame_color <= 200:
                self.Frame_color += 1

        else:
            if self.Frame_color >= 10:
                self.Frame_color -= 1
        pen = QPen(QColor(0, self.Frame_color, 0, 200))  # Создаем QPen с цветом
        pen.setWidth(int(np.log(self.Frame_color) * np.sin(
            self.Frame_color / 15) ** 2 + self.Frame_color / 50))  # Устанавливаем ширину пера
        painter.setPen(pen)  # Устанавливаем pen для painter
        painter.setBrush(Qt.GlobalColor.transparent)  # Устанавливаем прозрачную заливку

        # Рисуем прямоугольник с помощью painter
        if self.frame_show:
            painter.drawRect(QRect(3, 3, WIDTH - 5, HEIGHT - 50))

        if self.selected_window is not None:
            if self.selected_window.isMinimized is not False:
                painter.drawRect(QRect(
                    self.selected_window.left,
                    self.selected_window.top,
                    self.selected_window.width,
                    self.selected_window.height
                ))

        painter.end()
