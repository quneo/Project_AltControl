import pygetwindow as gw

class WindowActions:
    """Класс для работы с окнами"""
    @staticmethod
    def select_window(x, y):
        windows = gw.getWindowsAt(x, y)
        if not windows:
            return None
        print(windows)
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

    @staticmethod
    def restore_window():
        pass

    def close_window(self, x, y):
        window = self.select_window(x, y)
        window.minimize()
