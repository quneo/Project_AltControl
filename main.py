import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow  # Импортируем класс интерфейса

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  # Создаём экземпляр главного окна
    window.show()          # Показываем окно
    sys.exit(app.exec())   # Запускаем приложение
