import numpy as np
from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer

from colors import Frame_color, Hand_landmark_color
from controllers.activity_controller import ActivityController
from controllers.activity_performer import ActivityPerformer
from gestures.gesture_recognizer import GestureRecognizer
from utils.constants import connections
from utils.functions import bbox_cords
from gestures.gesture_list import gestures


class ActiveFrame(QMainWindow):
    def __init__(self, camera_index, model_quality, frame_show, bbox_show):
        super().__init__()
        self.pen_frame = QPen(QColor(0, Frame_color, 0, 200))
        self.bbox_show = bbox_show
        self.frame_show = frame_show
        self.model_quality = model_quality  # 0
        self.camera_index = camera_index
        self.finger_points = None
        self.cur_gesture = None
        self.Frame_color = Frame_color

        self.setup_window()
        self.init_pens_and_brushes()

        self.start_threads()

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

    def update_frame_pen(self):
        pen_width = int(np.log(self.Frame_color) * np.sin(self.Frame_color / 15) ** 2 + self.Frame_color / 50)
        self.pen_frame.setColor(QColor(0, self.Frame_color, 0))
        self.pen_frame.setWidth(pen_width)

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

        # Перо для ограничивающей рамки
        self.bbox_lines = QPen(QColor(0, 150, 0))
        self.bbox_lines.setWidth(2)

    def start_threads(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_tracking)  # Перерисовываем каждые 20 мс
        self.update_timer.start(20)

        self.gesture_thread = GestureRecognizer(self.WIDTH, self.HEIGHT, self.model_quality, self.camera_index)
        self.gesture_thread.gesture_signal.connect(self.on_gesture_detected)
        self.gesture_thread.start()

        self.activity_controller = ActivityController()
        self.activity_performer = ActivityPerformer()

        self.gesture_thread.gesture_signal.connect(self.activity_controller.on_gesture_detected)
        self.activity_controller.action_signal.connect(self.activity_performer.set_action)

        self.activity_controller.start()
        self.activity_performer.start()

    def update_tracking(self):
        self.update()

    def on_gesture_detected(self, result):
        self.finger_points = result[1]
        self.cur_gesture = result[0]

    def draw_frame(self, painter):
        """Рисует прямоугольную рамку на экране с плавной настройкой цвета и толщины линии."""
        painter.setPen(self.pen_frame)
        painter.setBrush(Qt.GlobalColor.transparent)
        painter.drawRect(QRect(3, 3, self.WIDTH - 5, self.HEIGHT - 50))

    def draw_hand_landmarks(self, painter, points):
        """Отрисовка ключевых точек руки и линий соединений между ними."""
        print(points)
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
        """Отрисовка ограничивающей рамки вокруг руки."""
        painter.setPen(self.bbox_lines)
        painter.setBrush(Qt.GlobalColor.transparent)
        bbox = bbox_cords(points)
        painter.drawRect(QRect(bbox[0], bbox[1], bbox[2], bbox[3]))
        text = gestures[self.cur_gesture]  # Текст, который нужно отобразить
        font = painter.font()  # Получаем текущий шрифт
        font.setPointSize(20)  # Устанавливаем размер шрифта
        painter.setFont(font)  # Применяем шрифт к painter
        painter.drawText(QPoint(bbox[0], bbox[1] - 10), text)

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.bbox_show:
            self.update_frame_pen()
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
