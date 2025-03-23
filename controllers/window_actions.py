import pygetwindow as gw
import time

class WindowActions:

    def __init__(self):
        self.current_window = None

    """Класс для работы с окнами"""
    def select_window(self, x, y):
        windows = gw.getWindowsAt(x, y)
        if not windows:
            return None
        window = windows[1]

        if not window.title.strip():
            return None
        return window
    
    def capture_window(self, x, y):
        window = self.select_window(x, y)
        if window is not None:
            self.current_window = window
            return True
        return False

    def move(self, dif_x, dif_y):
        """Перемещаем захваченное окно"""
        if self.current_window is not None:
            # Получаем текущие координаты окна
            current_x, current_y = self.current_window.left, self.current_window.top
            # Перемещаем окно с учетом смещения
            self.current_window.moveTo(current_x + dif_x, current_y + dif_y)

    def smooth_move(self, dif_x, dif_y, steps=10):
        """Плавное перемещение окна"""
        if self.current_window is not None and steps > 0:
            # Вычисляем шаги для плавного перемещения
            step_x = dif_x / steps
            step_y = dif_y / steps

            # Перемещаем окно шаг за шагом
            for _ in range(steps):
                self.move(int(step_x), int(step_y))  # Преобразуем в целые числа
                #time.sleep(0.05)  # Задержка для плавного перемещения

            # Корректируем конечное положение, чтобы избежать накопления ошибок
            final_x = int(dif_x - (step_x * steps))
            final_y = int(dif_y - (step_y * steps))
            self.move(final_x, final_y)

    def release_window(self):
        """Отпускаем окно (просто удаляем ссылку на текущее окно)"""
        self.current_window = None

    def restore_window(self):
        """Восстанавливаем окно"""
        if self.current_window is not None:
            self.current_window.restore()

    def minimize_window(self):
        if self.capture_window != None:
            self.current_window.minimize()
        self.release_window()
        
