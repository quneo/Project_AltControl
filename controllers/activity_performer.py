import time

from PyQt6 import QtCore

from controllers.mouse_actions import MouseActions
from controllers.window_actions import WindowActions


class ActivityPerformer(QtCore.QThread):
    """Класс для выполнения действий мыши."""
    def __init__(self):
        super().__init__()
        self.mouse_actions = MouseActions()
        self.window_actions = WindowActions()
        self.current_action = None

    def run(self):
        """Обработка действий в отдельном потоке."""
        while True:
            if self.current_action:
                self.execute_action(self.current_action)
            time.sleep(0.01)

    def set_action(self, action):
        """Устанавливает текущее действие для выполнения."""
        self.current_action = action

    def execute_action(self, action):
        """Выполняет заданное действие."""
        action_type = action.get('type')

        if action_type == 'click':
            self.mouse_actions.click(action['x'], action['y'], action.get('button'))
            self.current_action = None

        elif action_type == 'double_click':
            self.mouse_actions.double_click(action['x'], action['y'], action.get('button', 'left'))
            self.current_action = None

        elif action_type == 'lmb_down':
            self.mouse_actions.mouse_down(action['x'], action['y'], action.get('button'))

        elif action_type == 'follow':
            self.mouse_actions.move_to(action['x'], action['y'])

        elif action_type == 'lmb_up':
            self.mouse_actions.mouse_up(action.get('button'))
            self.current_action = None

        elif action_type == 'scroll':
            self.mouse_actions.scroll(action.get('scroll_param'))
            self.current_action = None

        elif action_type == 'close_window':
            self.window_actions.close_window(action.get('x'), action.get('y'))
            self.current_action = None


