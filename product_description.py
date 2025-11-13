import os
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QScrollArea, QFrame,
                             QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon
import settings
from styles import STYLES

class ProductDetails(QWidget):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.setStyleSheet(STYLES)
        self.setup_ui()

    def setup_ui(self):
        # Главный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # заголовок
        title_label = QLabel(self.text)
        title_label.setObjectName("description_name")
        # значение
        self.label = QLabel()
        self.label.setObjectName("description_text")

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.label)

class ProductImage(QLabel):
    def LoadImage (self, image_path):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Увеличиваем размер изображения для полноэкранного режима
            screen_size = QApplication.primaryScreen().availableSize()
            image_size = min(400, screen_size.height() // 2)
            pixmap = pixmap.scaled(image_size, image_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setFixedSize(image_size, image_size)
            self.setPixmap(pixmap)
        else:
            self.setText("Нет изображения")
            self.setAlignment(Qt.AlignCenter)
            self.setFixedSize(400, 400)

    def __init__(self):
        super().__init__()
        image_path = "no_foto.jpg"
        self.LoadImage(image_path)
        self.setAlignment(Qt.AlignCenter)
class ProductDescription(QWidget):
    closed_with_result = pyqtSignal(object)  # Изменено на object для возврата разных типов

    def __init__(self):
        super().__init__()
        self.price = None
        self.discount_price = None
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.on_inactivity_timeout)
        self.result_value = None  # Для хранения возвращаемого значения
        self.setStyleSheet(STYLES)
        self.setup_ui()
        self.setup_inactivity_timer()
    def setup_ui(self):

        # Главный layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Верхняя часть: изображение и основная информация
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)

        # Инградиенты
        ingradients_layout = QHBoxLayout()

        # Параметры
        descriptions_layout = QHBoxLayout()

        # Описание скидки
        discount_layout = QHBoxLayout()

        # Оплата
        pay_layout = QHBoxLayout()

        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(ingradients_layout)
        self.main_layout.addLayout(descriptions_layout)
        self.main_layout.addLayout(discount_layout)
        self.main_layout.addLayout(pay_layout)

        self.image_label = ProductImage()


        # Описание продукта
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName("product_description")
        # Инградиенты заголовок
        ingradients_title_label = QLabel()
        ingradients_title_label.setFixedWidth(300)
        ingradients_title_label.setObjectName("description_name")
        # Инградиенты текст
        self.ingradients_label = QLabel()
        self.ingradients_label.setWordWrap(True)
        self.ingradients_label.setObjectName("description_text")
        # Параметры: Вес
        self.description_weigth = ProductDetails("Вес:")
        #description_weigth. main_layout.label.setText("Вес:")
        # Параметры: Калорийность
        self.description_calory = ProductDetails("Калорийность:")
        #description_weigth.label.setText("Калорийность:")
        # Параметры: Срок хранения
        self.description_shelf_life = ProductDetails("Срок хранения:")
        #description_weigth.label.setText("Калорийность:")
        # Параметры: Время разогрева
        self.description_warm_time = ProductDetails("Время разогрева:")
        #description_weigth.label.setText("Калорийность:")
        # Описание скидки
        self.discount_label = QLabel()
        self.discount_label.setObjectName("discount_description")
        # Оплата
        self.discount_price_button = QPushButton()
        self.discount_price_button.setObjectName("discount_price_button")
        self.price_button = QPushButton()
        self.price_button.setObjectName("price_button")
        self.discount_price_button.setFixedHeight(settings.Settings.PAY_BUTTON_HEIGHT)
        self.price_button.setFixedHeight(settings.Settings.PAY_BUTTON_HEIGHT)
        self.price_button.clicked.connect(self.buy_normal)
        self.discount_price_button.clicked.connect(self.buy_with_discount)

        # Заполнение контента

        ingradients_title_label.setText("Инградиетны:")


        # Компановка виджетов
        top_layout.addWidget(self.image_label)
        top_layout.addWidget(self.description_label)
        ingradients_layout.addWidget(ingradients_title_label)
        ingradients_layout.addWidget(self.ingradients_label)
        descriptions_layout.addWidget(self.description_weigth)
        descriptions_layout.addWidget(self.description_calory)
        descriptions_layout.addWidget(self.description_shelf_life)
        descriptions_layout.addWidget(self.description_warm_time)
        discount_layout.addWidget(self.discount_label)
        pay_layout.addWidget(self.discount_price_button)
        pay_layout.addWidget(self.price_button)

        self.setLayout(self.main_layout)

    def load_data(self, data):
        self.description_label.setText(data['description'])
        self.ingradients_label.setText(data['ingredients'])
        self.description_weigth.label.setText(f"{data['weight']} грамм")
        self.description_calory.label.setText(f"{data['calorie']} кКал")
        self.description_shelf_life.label.setText(self.format_shelf_life(data['shelf_life']))
        self.description_warm_time.label.setText(self.format_warm_time(data['warm_time']))
        if data['discount_description']:
            self.discount_label.setText(f"Есть вариант этого товара со скидкой:\n{data['discount_description']}")
        if data['price']:
            self.price_button.setText(f"Купить за {data['price']:.2f} ₽")
        if data['discount_price']:
            self.discount_price_button.setText(f"Купить со скидкой за {data['discount_price']:.2f} ₽")
        self.image_label.LoadImage(f"{settings.Settings.PRODUCT_IMAGE_PATH}\\{data['guid']}.{data['extension']}")
        if data['discount_description'] and data['discount_price'] and 0 < data['discount_price'] < data['price']:
            self.discount_label.setVisible(True)
            self.discount_price_button.setVisible(True)
        else:
            self.discount_label.setVisible(False)
            self.discount_price_button.setVisible(False)
        self.price = data['price']
        self.discount_price = data['discount_price']

    def load_icon(self, icon_name):
        """Загрузка иконки из папки icons"""
        icon_path = os.path.join(settings.Settings.ICONS_PATH, icon_name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            print(f"Иконка не найдена: {icon_path}")
            return QIcon()

    def format_shelf_life(self, hours):
        days = hours // 24
        remaining_hours = hours % 24
        if days == 0:
            return f"{remaining_hours} час."
        else:
            if remaining_hours == 0:
                return f"{days} сут."
            else:
                return f"{days} сут. и {remaining_hours} час. "

    def format_warm_time(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if minutes == 0:
            return f"{remaining_seconds} сек."
        else:
            if remaining_seconds == 0:
                return f"{minutes} мин."
            else:
                return f"{minutes} мин. {remaining_seconds} сек."

    def get_image_path(self):
        guid = self.data.get('guid', '')
        extension = self.data.get('extension', '')
        if guid and extension:
            filename = f"{guid}{extension}"
            return os.path.join(settings.Settings.GOOD_IMAGE_PATH, filename)
        return ""

    def setup_inactivity_timer(self):
        self.inactivity_timer.start(settings.Settings.INACTIVITY_TIMEOUT * 1000)

    def reset_inactivity_timer(self):
        self.inactivity_timer.stop()
        self.inactivity_timer.start(settings.Settings.INACTIVITY_TIMEOUT * 1000)

    def stop_inactivity_timer(self):
        self.inactivity_timer.stop()

    def on_inactivity_timeout(self):
        self.result_value = None
        self.closed_with_result.emit(self.result_value)
        #self.reject()

    def buy_with_discount(self):
        self.stop_inactivity_timer()
        self.result_value = self.discount_price
        self.closed_with_result.emit(self.result_value)
        #self.accept()

    def buy_normal(self):
        self.stop_inactivity_timer()
        # Возвращаем обычную цену
        self.result_value = self.price
        self.closed_with_result.emit(self.result_value)
        #self.accept()

    def close_window(self):
        # При закрытии через кнопку "Вернуться в меню" возвращаем None
        self.result_value = None
        self.closed_with_result.emit(self.result_value)
        self.reject()

    def get_result(self):
        """Метод для получения результата после закрытия окна"""
        return self.result_value

    def showEvent(self, event):
        """Гарантируем полноэкранный режим при показе окна"""
        super().showEvent(event)
        # Дополнительная проверка - если окно не в полноэкранном режиме, переключаем
        if not self.isFullScreen():
            self.showFullScreen()

    def mousePressEvent(self, event):
        self.reset_inactivity_timer()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self.reset_inactivity_timer()
        # Закрытие по Escape - возвращаем None
        if event.key() == Qt.Key_Escape:
            self.close_window()
        super().keyPressEvent(event)