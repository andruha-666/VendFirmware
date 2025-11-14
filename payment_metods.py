import os
import sys
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QScrollArea, QFrame,
                             QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon
import settings
from styles import STYLES


class PaymentMetods(QWidget):
    closed_with_result = pyqtSignal(object)  # Изменено на object для возврата разных типов
    summa = 500.99
    def __init__(self, data):
        super().__init__()
        self.price = None
        self.discount_price = None
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.on_inactivity_timeout)
        self.result_value = None  # Для хранения возвращаемого значения
        self.setStyleSheet(STYLES)
        self.data = data
        self.setup_ui()
        self.remaining_time = 0
        self.setup_inactivity_timer()
    def setup_ui(self):

        # Главный layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Верхняя часть: сумма к оплате
        summa_layout = QVBoxLayout()
        summa_layout.setSpacing(10)
        summa_layout.setAlignment(Qt.AlignCenter)

        # Надпись "Сумма к оплате"
        summa_title = QLabel("Сумма к оплате")
        summa_title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #ffffff;")
        summa_title.setAlignment(Qt.AlignCenter)

        # Сумма
        self.summa_label = QLabel()
        self.summa_label.setStyleSheet("font-size: 32pt; font-weight: bold; color: #27ae60;")
        self.summa_label.setAlignment(Qt.AlignCenter)

        summa_layout.addWidget(summa_title)
        summa_layout.addWidget(self.summa_label)

        self.main_layout.addLayout(summa_layout)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #444; margin: 20px 0;")
        separator.setFixedHeight(2)
        self.main_layout.addWidget(separator)

        self.main_layout.addLayout(summa_layout)

        # Сетка для кнопок способов оплаты
        payment_grid_layout = QGridLayout()
        payment_grid_layout.setSpacing(20)
        payment_grid_layout.setHorizontalSpacing(30)
        payment_grid_layout.setVerticalSpacing(20)

        # Добавляем сетку в основной layout
        payment_grid_widget = QWidget()
        payment_grid_widget.setLayout(payment_grid_layout)
        self.main_layout.addWidget(payment_grid_widget)

        data_len = len(self.data)
        if len(self.data) <= 3:
            col = 0
        elif 3 < data_len <= 6:
            col = 1
        else:
            col = 2
        print(col)
        cur_col = 0
        cur_row = 0

        for data_item in self.data:
            payment_button = self.create_payment_button(data_item)
            payment_grid_layout.addWidget(payment_button, cur_row, cur_col)
            if cur_col == col:
                cur_col = 0
                cur_row = cur_row + 1
            else:
                cur_col = cur_col + 1

        self.main_layout.addStretch()
        self.timer_layout = QHBoxLayout()
        self.timer_layout.addStretch()
        self.remaining_time_label = QLabel()
        self.remaining_time_label.setObjectName("remaining_time_label")
        self.timer_layout.addWidget(self.remaining_time_label)
        self.timer_layout.addStretch()
        self.main_layout.addLayout(self.timer_layout)
        self.setLayout(self.main_layout)

    def set_price(self, price):
        self.summa = price
        self.summa_label.setText(f"{self.summa:.2f} ₽")
    def create_payment_button(self, data):
        """Создает кнопку для способа оплаты"""
        button = QPushButton(data[2])
        button.setObjectName("payment_metod")
        metod_id = data[1]
        # Загружаем иконку
        icon_path = os.path.join(settings.Settings.ICONS_PATH, f"{data[1]}.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            button.setIcon(icon)
            button.setIconSize(QSize(100, 100))
        else:
            print(f"Иконка способа оплаты не найдена: {icon_path}")

        # Привязываем обработчик нажатия
        button.clicked.connect(lambda checked, method_id=data[0]: self.select_payment_metod(metod_id))

        return button

    def load_icon(self, icon_name):
        """Загрузка иконки из папки icons"""
        icon_path = os.path.join(settings.Settings.ICONS_PATH, icon_name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"Иконка не найдена: {icon_path}")
            return QIcon()

    def setup_inactivity_timer(self):
        self.remaining_time = settings.Settings.INACTIVITY_TIMEOUT
        self.inactivity_timer.start(1000)

    def stop_inactivity_timer(self):
        self.inactivity_timer.stop()

    def on_inactivity_timeout(self):
        self.remaining_time = self.remaining_time - 1
        self.remaining_time_label.setText(f"Окно закроется через {self.remaining_time} сек.")
        self.inactivity_timer.start(1000)
        if self.remaining_time == 0:
            self.result_value = None
            self.closed_with_result.emit(None)
            self.stop_inactivity_timer()

    def select_payment_metod(self, metod_id):
        print(metod_id)
        self.stop_inactivity_timer()
        self.closed_with_result.emit(metod_id)

    def showEvent(self, event):
        """Гарантируем полноэкранный режим при показе окна"""
        super().showEvent(event)
        # Дополнительная проверка - если окно не в полноэкранном режиме, переключаем
        if not self.isFullScreen():
            self.showFullScreen()
