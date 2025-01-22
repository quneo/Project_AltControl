import numpy as np

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