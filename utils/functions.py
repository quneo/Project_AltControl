import numpy as np
from settings import *

def bbox_cords(points):
    points = np.array(points)  # Преобразуем список в массив numpy

    # Находим минимальные и максимальные координаты
    x_min = points[:, 0].min()
    y_min = points[:, 1].min()
    x_max = points[:, 0].max()
    y_max = points[:, 1].max()

    # Создаем прямоугольник с правильными размерами
    width = x_max - x_min
    height = y_max - y_min

    # Добавляем отступы
    padding_x = width * 0.03
    padding_y = height * 0.03

    x_min -= padding_x
    y_min -= padding_y
    width += 2 * padding_x  # Увеличиваем ширину на 6% по обеим сторонам
    height += 2 * padding_y  # Увеличиваем высоту на 6% сверху и снизу

    return int(x_min), int(y_min), int(width), int(height)

def fingers_bias(fingers):
    center_x, center_y = int(np.mean(fingers[:, 0])), int(np.mean(fingers[:, 1]))
    fingers_biased = fingers.copy()

    def calculate_bias(x, y):
        softing = 1
        return np.array([x - WIDTH // 2, y - HEIGHT // 2]) // softing

    bias = calculate_bias(center_x, center_y)
    fingers_biased[:, 0] += bias[0]
    fingers_biased[:, 1] += bias[1]

    return fingers_biased
