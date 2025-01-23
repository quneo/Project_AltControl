import math
import numpy as np

def dist(x0, y0, x1, y1):
    result = np.linalg.norm(np.array([x1, y1]) - np.array([x0, y0]))
    return result


def classification(fingers_cords, model):
    fingers_unif = prepare_for_model(fingers_cords)
    res = model(fingers_unif)

    return res


def prepare_for_model(fingers_cords):
    fingers_rot = unificate_hand(fingers_cords)[0]  # Унифицируем ладонь
    fingers_rot = fingers_rot - fingers_cords[0]    # Переносим центр С.К. в (x0, y0)

    fingers_x = fingers_rot[:, 0]
    fingers_y = fingers_rot[:, 1]

    fingers_x = normalize(fingers_x)
    fingers_y = normalize(fingers_y)

    fingers_x = fingers_x[1:]
    fingers_y = fingers_y[1:]

    fingers_unif = np.expand_dims(np.concatenate([fingers_x, fingers_y]).T, axis=0)

    return fingers_unif


def normalize(x):
    x1 = x / x.std()
    return x1


def unificate_hand(fingers_cords: np.array):    # Отзеркалена, повернута.
    mirror_flag = define_orientation(fingers_cords)  # Проверяем направленность ладони
    if mirror_flag == -1:
        fingers_cords = mirror_hand(fingers_cords)  # При необходимости отражаем координаты кисти

    alpha = calculate_angle(fingers_cords)  # Вычисляем угол наклона ладони

    center_x, center_y = fingers_cords[0]  # Сохраняем точку 0
    # Для корректного наклона руки относительно точки 0 нереносим центр С.К. в точку 0
    fingers_cords_transfered = transfer_fingers(fingers_cords, fingers_cords[0])

    # Применяем оператор поворота
    rotation_matrix = np.array([[np.cos(-alpha), -np.sin(-alpha)],
                                [np.sin(-alpha), np.cos(-alpha)]])

    fingers_rot = np.dot(fingers_cords_transfered, rotation_matrix)

    # Возвращаем центр С.К. назад
    fingers_rot += np.array([center_x, center_y])

    return fingers_rot.astype(int), alpha


def calculate_angle(fingers_cords: np.array) -> float:  # Вычисление угла наклона ладони
    delta = fingers_cords[13] - fingers_cords[9]  # Координаты разности
    temp1 = delta[0]  # x-координата разности
    temp2 = np.linalg.norm(delta)  # длина вектора

    if temp2 == 0:  # Избегаем деления на ноль
        return 0

    angle = np.arccos(temp1 / temp2)  # Вычисляем угол
    orient = np.sign(fingers_cords[0][0] - fingers_cords[13][0])  # Определяем ориентацию наклона
    angle *= np.sign(orient)

    return angle


def define_orientation(fingers_cords: np.array) -> int:
    finger_0 = fingers_cords[0]
    finger_9 = fingers_cords[9]
    finger_13 = fingers_cords[13]

    # Вычисляем компоненты
    delta_x_9 = finger_9[0] - finger_0[0]
    delta_y_13 = finger_13[1] - finger_0[1]
    delta_y_9 = finger_9[1] - finger_0[1]
    delta_x_13 = finger_13[0] - finger_0[0]

    # Третья координата векторного произведения
    z_comp = delta_x_9 * delta_y_13 - delta_y_9 * delta_x_13

    return np.sign(z_comp)  # 1 - ладонь в камеру, -1 - ладонь в лицо


def mirror_hand(fingers_cords: np.array) -> np.array:
    symmerty_point = fingers_cords[0][0]

    mirrored_cord = fingers_cords.copy()

    mirrored_cord[1:, 0] += 2 * (symmerty_point - fingers_cords[1:, 0])

    return mirrored_cord


def transfer_fingers(fingers_cords: np.array, center: np.array) -> np.array:
    fingers_transfer = fingers_cords - center
    return fingers_transfer


def return_normalized_points(fingers_cords):
    fingers_x = fingers_cords[:, 0]
    fingers_y = fingers_cords[:, 1]

    fingers_x = (fingers_x - fingers_x.mean()) / fingers_x.std()
    fingers_y = (fingers_y - fingers_y.mean()) / fingers_y.std()

    fingers_norm = np.dstack((fingers_x, fingers_y))

    return fingers_norm[0]

def calculate_absangle(fingers_cords):
    mirror_flag = define_orientation(fingers_cords)
    if mirror_flag == -1:
        fingers_cords = mirror_hand(fingers_cords)

    temp1 = fingers_cords[13][0] - fingers_cords[9][0]
    temp2 = math.sqrt(
        math.pow((fingers_cords[13][1] - fingers_cords[9][1]), 2) + math.pow(
            (fingers_cords[13][0] - fingers_cords[9][0]), 2))

    angle = np.arccos(temp1 / temp2)
    orient = np.sign(fingers_cords[0][0] - fingers_cords[13][0])
    angle *= np.sign(orient)

    if mirror_flag == -1:
        angle *= mirror_flag

    return angle

def conversion_to_degrees(angle):
    angle_degrees = round((angle / math.pi * 180), 2)
    return angle_degrees

