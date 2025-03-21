import pyautogui
import time

class KeyboardActions:
    alttab_active = False  # Флаг активности alt-tab

    @staticmethod
    def open_alttab():
        if not KeyboardActions.alttab_active:
            pyautogui.keyDown("alt")
            time.sleep(0.1)
            pyautogui.press("tab")
            KeyboardActions.alttab_active = True

    @staticmethod
    def close_alttab():
        if KeyboardActions.alttab_active:
            time.sleep(0.1)  # Имитируем задержку перед отпусканием Alt
            pyautogui.keyUp("alt")
            KeyboardActions.alttab_active = False

    @staticmethod
    def next_window():
        if KeyboardActions.alttab_active:
            pyautogui.press("tab")          

    @staticmethod
    def minimize_all():
        pyautogui.hotkey('win', 'd')



