from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt


class ActiveFrame(QWidget):
    def __init__(self, camera_index, model_quality, frame_show, bbox_show):
        super().__init__()
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Пример рисования рамки и проекции руки
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawRect(50, 50, 300, 300)  # Пример рамки

        # Здесь можно добавить код для рисования рук, ключевых точек и т.д.
        # Например, рисуем точки (предположим, что это ключевые точки на руке)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(150, 150, 10, 10)  # Пример точки
        painter.drawEllipse(200, 200, 10, 10)  # Пример точки
        painter.end()
