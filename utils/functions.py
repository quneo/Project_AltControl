import numpy as np
from settings import *
from utils.unificate_cords import conversion_to_degrees, dist


def get_bbox(points):
    """
    По ключевым точкам строим координаты ограничивающей рамки в формате (x_min, y_min, x_max, y_max).

    :param points: Ключевые точки
    """
    scale_factor = 1.2    # Коэффициент растягивания рамки
    x_min, y_min = np.min(points[:, 0]), np.min(points[:, 1])
    x_max, y_max = np.max(points[:, 0]), np.max(points[:, 1])

    width = x_max - x_min
    height = y_max - y_min

    
    new_width = width * scale_factor
    new_height = height * scale_factor

    new_x_min = x_min - (new_width - width) / 2
    new_y_min = y_min - (new_height - height) / 2
    new_x_max = x_max + (new_width - width) / 2
    new_y_max = y_max + (new_height - height) / 2

    
    return np.array([new_x_min, new_y_min, new_x_max, new_y_max]).reshape(-1,2)

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


def scroll_angle(points):
    # Координаты точек 5 и 8
    x5, y5 = points[5]
    x8, y8 = points[8]

    # Угол в радианах
    angle = np.arctan2(y8 - y5, x8 - x5)

    if angle < 0:
        angle += 2 * np.pi

    return np.degrees(angle) - 180


def scroll_param(degree):
    a, b = 25, 33
    c = 20

    if degree > a:
        return int(c * np.log(degree - a + 1))
    elif degree < -b:
        return int(-c * np.log(-degree - b + 1))
    else:
        return 0


def is_close(point1, point2, threshold=0.45):
    """Проверяет, находятся ли две точки ближе заданного расстояния."""
    return dist(point1[0], point1[1], point2[0], point2[1]) <= threshold
