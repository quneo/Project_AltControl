from PyQt6.QtGui import QPainter, QPolygon, QColor, QBrush
from PyQt6.QtCore import QPoint, Qt

from ui.polygon_edge import fingers, edges, palm_poly, polygons, calculate_light_intensity, blue_shades, green_colors
from utils.constants import connections
import math
import numpy as np


def draw_hand_landmarks(painter: QPainter, points, pen_landmarks, brush_landmarks, pen_lines):
    """Отрисовка ключевых точек руки и линий соединений между ними."""
    painter.setPen(pen_landmarks)
    painter.setBrush(brush_landmarks)

    for point in points:
        painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)  # Радиус эллипсов = 7

    painter.setPen(pen_lines)
    # Рисуем линии между точками (если есть соединения)
    for connection in connections:
        painter.drawLine(
            QPoint(points[connection[0]][0], points[connection[0]][1]),
            QPoint(points[connection[1]][0], points[connection[1]][1])
        )


def extra_points(point1, point2):
    """Функция для вычисления дополнительных точек вокруг пальцев."""

    x1, y1 = point1
    x2, y2 = point2
    norm = np.array([y2 - y1, x1 - x2]) / math.sqrt(math.pow(y2 - y1, 2) + math.pow(x1 - x2, 2))

    distance = np.linalg.norm(point1 - point2)
    factor_a = np.log(distance) * 4

    extra_point1 = point1 + factor_a * norm
    extra_point2 = point1 - factor_a * norm

    return np.array([extra_point1, extra_point2])


def extra_points2(point1, point2, a):
    """Выпуклая линейная комбинация. Используется для заолнения кисти"""
    extra_point = a * point1 + (1 - a) * point2
    return extra_point


def fingertip(point1, point2, a, b):
    """Округление кончиков пальцев"""
    x1, y1 = point1
    x2, y2 = point2
    norm = np.array([y2 - y1, x1 - x2]) / math.sqrt(math.pow(y2 - y1, 2) + math.pow(x1 - x2, 2))

    X1 = 0.25 * point1 + 0.75 * point2
    extra_point1 = X1 + a * norm

    X2 = 0.75 * point1 + 0.25 * point2
    extra_point2 = X2 + a * norm

    X3 = 0.5 * (point1 + point2)
    extra_point3 = X3 + b * norm

    return np.vstack((extra_point1, extra_point2, extra_point3))


def calculate_vertexes(points):
    vertex = points

    # Обработка пальцев
    for finger in fingers:
        for i in range(len(finger[1:])):
            pair = extra_points(points[finger[1:][i]], points[finger[1:][i - 1]])
            vertex = np.vstack((vertex, pair)).astype(int)

    # Обработка ладони
    palm_points = np.array([]).reshape(0, 2)
    palm_pairs = [
        (0, 29, 0.7), (0, 29, 0.4),
        (0, 37, 0.3), (0, 37, 0.8),
        (0, 45, 0.6), (0, 45, 0.2),
        (0, 54, 0.6), (0, 54, 0.3)
    ]

    for p1, p2, factor in palm_pairs:
        vertex = np.vstack((vertex, extra_points2(vertex[p1], vertex[p2], factor)))

    palm_points = palm_points.astype(int)
    vertex = np.vstack((vertex, palm_points))

    # Обработка кончиков пальцев
    fingertip_pairs = [(27, 28), (35, 36), (43, 44), (51, 52), (59, 60)]
    for p1, p2 in fingertip_pairs:
        vertex = np.vstack((vertex, fingertip(vertex[p1], vertex[p2], -15, -17)))

    return vertex.astype(int)


def draw_hand_polygon(painter: QPainter, points, pen_landmarks, brush_landmarks, pen_lines):
    vertex = calculate_vertexes(points)
    """Отрисовка ключевых точек руки и линий соединений между ними."""
    painter.setPen(pen_landmarks)
    painter.setBrush(brush_landmarks)

    for point in vertex:
        painter.drawEllipse(QPoint(point[0], point[1]), 2, 2)  # Радиус эллипсов = 7

    painter.setPen(pen_lines)
    # Рисуем линии между точками (если есть соединения)
    for edge in edges:
        for connection in edge:
            painter.drawLine(
                QPoint(vertex[connection[0]][0], vertex[connection[0]][1]),
                QPoint(vertex[connection[1]][0], vertex[connection[1]][1])
            )


def draw_hand_triangles(painter: QPainter, points, pen_landmarks, brush_landmarks, pen_lines):
    """Отрисовка залитых треугольников с разными оттенками синего."""
    vertex = calculate_vertexes(points)
    painter.setPen(Qt.PenStyle.NoPen)  # Убираем контур

    for i, polygon in enumerate(polygons):
        for j, tri in enumerate(polygon):
            color = green_colors[i*j % len(green_colors)]  # Выбор цвета по кругу
            painter.setBrush(color)

            poly = QPolygon([QPoint(vertex[j][0], vertex[j][1]) for j in tri])
            painter.drawPolygon(poly)

    # Отрисовка точек
    painter.setBrush(QColor(255, 255, 255))  # Белый цвет для точек
    for point in points:
        painter.drawEllipse(QPoint(point[0], point[1]), 3, 3)  # Радиус = 7

    painter.setPen(QColor(255, 255, 255))
    # Рисуем линии между точками (если есть соединения)
    for connection in connections:
        painter.drawLine(
            QPoint(points[connection[0]][0], points[connection[0]][1]),
            QPoint(points[connection[1]][0], points[connection[1]][1])
        )


