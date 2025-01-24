import time
import pyautogui
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer

from utils.unificate_cords import return_normalized_points, dist, conversion_to_degrees, calculate_absangle
from controllers.mouse_actions import MouseActions
class ActivityPerformer(QtCore.QThread):
    """Класс для выполнения действий мыши."""
    def __init__(self):
        super().__init__()
        self.mouse_actions = MouseActions()
        self.current_action = None

    def run(self):
        """Обработка действий в отдельном потоке."""
        while True:
            if self.current_action:
                self.execute_action(self.current_action)
                self.current_action = None
            time.sleep(0.01)

    def set_action(self, action):
        """Устанавливает текущее действие для выполнения."""
        self.current_action = action

    def execute_action(self, action):
        """Выполняет заданное действие."""
        action_type = action.get('type')

        if action_type == 'click':
            self.mouse_actions.click(action['x'], action['y'], action.get('button', 'left'))
