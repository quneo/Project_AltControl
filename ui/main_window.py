from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic.properties import QtCore
from PyQt6 import QtCore

import sys

from ui.ui_main import Ui_Form
from utils.camera import get_available_cameras
from ui.active_frame import ActiveFrame




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.available_cameras = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.menu_stat = [self.ui.Status_1, self.ui.Status_2, self.ui.Status_3, self.ui.Status_4]

        # Переменные для хранения текущих настроек
        self.camera_index = 1
        self.model_quality = 1    # 0 - high, 1 - amazing
        self.frame_show = True
        self.bbox_show = True

        # Флаг для отслеживания состояния окна
        self.is_frame_active = False

        # Настройка окна
        self.setup_window()

        # Настройка интерфейса
        self.setup_menu_buttons()
        self.setup_camera_settings()
        self.setup_model_quality()
        self.setup_frame_settings()

        # Объект для активного окна (активная рамка)
        self.frame_app = None

        # Задаем область для перетаскивания окна (например, верхние 40 пикселей)
        self.drag_area_height = 80
        self.old_position = None

    def setup_window(self):
        """Настройка внешнего вида окна."""
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.menu_stat[0].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")

    def setup_menu_buttons(self):
        """Настройка кнопок меню."""
        self.ui.Menu_button1.clicked.connect(self.select_menu)
        self.ui.Menu_button2.clicked.connect(self.select_menu)
        self.ui.Menu_button3.clicked.connect(self.select_menu)
        self.ui.Menu_button4.clicked.connect(self.select_menu)
        self.ui.pushButton.clicked.connect(self.start_application)  # Кнопка для запуска приложения
        self.ui.pushButton_3.clicked.connect(self.close_window)
        self.ui.pushButton_4.clicked.connect(self.minimize_window)

    def minimize_window(self):
        """Минимизация окна."""
        self.showMinimized()

    def close_window(self):
        """Закрытие окна приложения."""
        self.close()
        sys.exit()

    def setup_camera_settings(self):
        """Настройка камеры."""
        self.available_cameras = get_available_cameras()
        self.ui.camera_box.addItems(map(str, self.available_cameras))
        self.ui.camera_box.setCurrentIndex(0)
        self.ui.camera_box.currentIndexChanged.connect(self.update_camera_index)

    def setup_model_quality(self):
        """Настройка качества модели."""
        self.ui.select_quality.addItems(['high', 'amazing'])
        self.ui.select_quality.setCurrentIndex(0)
        self.ui.select_quality.currentIndexChanged.connect(self.change_model)

    def setup_frame_settings(self):
        """Настройка отображения рамки и боксов."""
        self.ui.show_frame.addItems(['True', 'False'])
        self.ui.show_frame.setCurrentIndex(0)
        self.ui.show_frame.currentIndexChanged.connect(self.change_frame_showing)

        self.ui.bbox_show.addItems(['True', 'False'])
        self.ui.bbox_show.setCurrentIndex(0)
        self.ui.bbox_show.currentIndexChanged.connect(self.change_bbox_show)

    def change_bbox_show(self, index):
        """Изменение отображения бокса."""
        self.bbox_show = index == 0

    def change_frame_showing(self, index):
        """Изменение отображения рамки."""
        self.frame_show = index == 0

    def change_model(self, index):
        """Изменение модели для распознавания жестов."""
        self.model_quality = index

    def update_camera_index(self, index):
        """Обновление индекса выбранной камеры."""
        self.camera_index = index

    def select_menu(self):
        """Обработчик выбора меню."""
        clicked_button = self.sender()

        # Сброс стилей всех кнопок
        for stat in self.menu_stat:
            stat.setStyleSheet("QFrame{background-color: rgb(43, 45, 48);border-radius :12px;}")

        # Выбор текущей кнопки
        if clicked_button is self.ui.Menu_button1:
            self.menu_stat[0].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(0)
        elif clicked_button is self.ui.Menu_button2:
            self.menu_stat[1].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(1)
        elif clicked_button is self.ui.Menu_button3:
            self.menu_stat[2].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(2)
        elif clicked_button is self.ui.Menu_button4:
            self.menu_stat[3].setStyleSheet("QFrame{background-color: rgb(0, 191, 255);border-radius :12px;}")
            self.ui.stackedWidget.setCurrentIndex(3)

    def start_application(self):
        """Запуск приложения с выбранными настройками, или закрытие активной рамки, если она уже есть."""
        if self.is_frame_active:
            # Если окно активно, закрываем его
            if self.frame_app:
                self.frame_app.close()
            self.is_frame_active = False  # Сбрасываем флаг
        else:
            # Если окно не активно, создаем новое
            if self.frame_app:
                self.frame_app.close()  # Закрыть предыдущее окно, если оно существует

            print(f"{self.camera_index, self.model_quality, self.frame_show, self.bbox_show}")

            # Создание нового окна с текущими настройками
            self.frame_app = ActiveFrame(
                camera_index=self.camera_index,
                model_quality=self.model_quality,
                frame_show=self.frame_show,
                bbox_show=self.bbox_show
            )
            self.frame_app.show()  # Показываем окно
            self.is_frame_active = True  # Устанавливаем флаг, что окно активно

    def mousePressEvent(self, event):
        """Обработчик нажатия кнопки мыши (для перемещения окна)."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Проверяем, что клик был в верхней части окна
            #print(event.pos().y(), self.drag_area_height)
            if event.pos().y() < self.drag_area_height:
                self.old_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Обработчик движения мыши (для перемещения окна)."""
        if self.old_position and event.pos().y() < self.drag_area_height:
            delta = event.globalPosition().toPoint() - self.old_position
            self.move(self.pos() + delta)
            self.old_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        """Обработчик отпускания кнопки мыши."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_position = None



