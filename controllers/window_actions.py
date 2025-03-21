import pygetwindow as gw
import time

class WindowActions:
    """Класс для работы с окнами"""
    @staticmethod
    def select_window(x, y):
        windows = gw.getWindowsAt(x, y)
        if not windows:
            return None
        window = windows[1]

        if not window.title.strip():
            return None
        return window

    def move(self, x, y, dif_x, dif_y):
        if dif_x != 0 and dif_y != 0:
            window = self.select_window(x, y)
            if window is not None:
                window.moveRel(dif_x, dif_y)
        else:
            pass

    def smooth_move(self, x, y, dif_x, dif_y, steps=10):
        """
        Плавно перемещает окно на указанное расстояние.
        :param x: Координата X для выбора окна.
        :param y: Координата Y для выбора окна.
        :param dif_x: Смещение по X.
        :param dif_y: Смещение по Y.
        :param duration: Длительность анимации в секундах.
        :param steps: Количество шагов анимации.
        """
        if dif_x != 0 and dif_y != 0:
            window = self.select_window(x, y)
            if window is not None:
                # Вычисляем шаги для плавного перемещения
                step_x = dif_x / steps
                step_y = dif_y / steps

                # Плавно перемещаем окно
                for _ in range(steps):
                    window.moveRel(int(step_x), int(step_y))
                    #time.sleep(delay)

    @staticmethod
    def restore_window():
        pass

    def minimize_window(self, x, y):
        window = self.select_window(x, y)
        if window is not None:
            window.minimize()
