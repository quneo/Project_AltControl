import pygetwindow as gw

class WindowActions:
    """Класс для работы с окнами"""
    @staticmethod
    def select_window(x, y):
        window = gw.getWindowsAt(x, y)[1]
        return window
    @staticmethod
    def move():
        pass
    @staticmethod
    def restore_window():
        pass

    def close_window(self, x, y):
        window = self.select_window(x, y)
        window.minimize()
