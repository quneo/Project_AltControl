import pyautogui


class MouseActions:
    """Класс для работы с мышью: клики, перемещения, скроллинг."""

    @staticmethod
    def move_to(x, y):
        pyautogui.moveTo(x, y)

    @staticmethod
    def click(x, y, button='left'):
        pyautogui.moveTo(x, y)
        pyautogui.click(button=button)

    @staticmethod
    def double_click(x, y, button='left'):
        pyautogui.moveTo(x, y)
        pyautogui.doubleClick(button=button)

    @staticmethod
    def scroll(angle):
        pyautogui.scroll(angle)

    @staticmethod
    def mouse_down(x, y, button='left'):
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown(button=button)

    @staticmethod
    def mouse_up(button='left'):
        pyautogui.mouseUp(button=button)
