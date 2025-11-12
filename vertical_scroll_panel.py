from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QScrollArea,
                             QSizePolicy, QScroller, QScrollerProperties, QMessageBox)
from PyQt5.QtGui import QPixmap, QMouseEvent, QKeyEvent, QPainter, QIcon, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QEvent, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets

from styles import STYLES
from settings import Settings
import time
from visual_elements import ClickableLabel

class VerticalScrollPanel(QWidget):
    gallery_data = []

    item_clicked = pyqtSignal(str)  # guid, item_data

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setStyleSheet(STYLES)
        self.setup_ui()
        self.setup_swipe_gestures()
        self.setup_animation()
        self.setup_inactivity_timer()  # Добавляем таймер бездействия

    def setup_ui(self):
        self.gallery_layout = QVBoxLayout(self)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_content)
        self.gallery_layout.addWidget(self.scroll_area)

    def setup_inactivity_timer(self):
        """Настройка таймера бездействия"""
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.on_inactivity_timeout)
        self.reset_inactivity_timer()

    def reset_inactivity_timer(self):
        """Сброс таймера бездействия"""
        self.inactivity_timer.start(self.settings.INACTIVITY_TIMEOUT * 1000)

    def stop_inactivity_timer(self):
        self.inactivity_timer.stop()

    def on_inactivity_timeout(self):
        """Обработка таймаута бездействия - эмитируем клик с None"""
        # print("Таймер бездействия - эмитируем клик с None")
        self.item_clicked.emit(None)

    def setup_swipe_gestures(self):
        self.scroll_area.setAttribute(Qt.WA_AcceptTouchEvents)
        self.scroll_content.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setAttribute(Qt.WA_AcceptTouchEvents)

        self.swipe_start_pos = None
        self.swipe_start_time = None
        self.last_pos = None
        self.last_time = None
        self.velocity = 0
        self.is_swiping = False
        self.click_threshold = 10
        self.max_click_time = 0.3

    def setup_animation(self):
        self.inertia_timer = QTimer()
        self.inertia_timer.timeout.connect(self.update_inertia)
        self.inertia_timer.setInterval(16)

    def event(self, event: QEvent) -> bool:
        # Сбрасываем таймер бездействия при любом пользовательском взаимодействии
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove,
                            QEvent.MouseButtonRelease, QEvent.TouchBegin,
                            QEvent.TouchUpdate, QEvent.TouchEnd]:
            self.reset_inactivity_timer()

        if event.type() == QEvent.TouchBegin:
            return self.handle_touch_begin(event)
        elif event.type() == QEvent.TouchUpdate:
            return self.handle_touch_update(event)
        elif event.type() == QEvent.TouchEnd:
            return self.handle_touch_end(event)
        elif event.type() == QEvent.MouseButtonPress:
            return self.handle_mouse_press(event)
        elif event.type() == QEvent.MouseMove:
            return self.handle_mouse_move(event)
        elif event.type() == QEvent.MouseButtonRelease:
            return self.handle_mouse_release(event)
        else:
            return super().event(event)

    def handle_touch_begin(self, event: QEvent) -> bool:
        if event.touchPoints():
            self.stop_inertia()
            self.reset_inactivity_timer()  # Сбрасываем таймер
            self.swipe_start_pos = event.touchPoints()[0].pos()
            self.swipe_start_time = time.time()
            self.last_pos = self.swipe_start_pos
            self.last_time = self.swipe_start_time
            self.is_swiping = False
            self.velocity = 0
            return True
        return False

    def handle_touch_update(self, event: QEvent) -> bool:
        if not self.swipe_start_pos or not event.touchPoints():
            return False

        current_pos = event.touchPoints()[0].pos()
        current_time = time.time()

        delta_x = abs(current_pos.x() - self.swipe_start_pos.x())
        delta_y = abs(current_pos.y() - self.swipe_start_pos.y())

        if delta_y > self.click_threshold or delta_x > self.click_threshold:
            self.is_swiping = True
            self.reset_inactivity_timer()  # Сбрасываем таймер при движении

        if self.is_swiping:
            self.process_swipe_gesture(self.last_pos, current_pos, current_time)
            return True

        self.last_pos = current_pos
        self.last_time = current_time
        return False

    def handle_touch_end(self, event: QEvent) -> bool:
        if not self.swipe_start_pos:
            return True

        current_time = time.time()
        gesture_duration = current_time - self.swipe_start_time

        if self.is_swiping:
            if abs(self.velocity) > 10:
                self.start_inertia()
        else:
            end_pos = event.touchPoints()[0].pos() if event.touchPoints() else self.swipe_start_pos
            delta_x = abs(end_pos.x() - self.swipe_start_pos.x())
            delta_y = abs(end_pos.y() - self.swipe_start_pos.y())

            if (delta_x <= self.click_threshold and
                    delta_y <= self.click_threshold and
                    gesture_duration <= self.max_click_time):
                self.handle_click(self.swipe_start_pos)

        self.is_swiping = False
        self.swipe_start_pos = None
        self.reset_inactivity_timer()  # Сбрасываем таймер после жеста
        return True

    def handle_mouse_press(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.LeftButton:
            self.stop_inertia()
            self.reset_inactivity_timer()  # Сбрасываем таймер
            self.swipe_start_pos = event.pos()
            self.swipe_start_time = time.time()
            self.last_pos = self.swipe_start_pos
            self.last_time = self.swipe_start_time
            self.is_swiping = False
            self.velocity = 0
            return True
        return False

    def handle_mouse_move(self, event: QMouseEvent) -> bool:
        if self.swipe_start_pos and event.buttons() & Qt.LeftButton:
            current_pos = event.pos()
            current_time = time.time()

            delta_x = abs(current_pos.x() - self.swipe_start_pos.x())
            delta_y = abs(current_pos.y() - self.swipe_start_pos.y())

            if delta_y > self.click_threshold or delta_x > self.click_threshold:
                self.is_swiping = True
                self.reset_inactivity_timer()  # Сбрасываем таймер при движении

            if self.is_swiping:
                self.process_swipe_gesture(self.last_pos, current_pos, current_time)
                return True

            self.last_pos = current_pos
            self.last_time = current_time
            return False
        return False

    def handle_mouse_release(self, event: QMouseEvent) -> bool:
        if not self.swipe_start_pos:
            return False

        current_time = time.time()
        gesture_duration = current_time - self.swipe_start_time

        if self.is_swiping:
            if abs(self.velocity) > 10:
                self.start_inertia()
        else:
            delta_x = abs(event.pos().x() - self.swipe_start_pos.x())
            delta_y = abs(event.pos().y() - self.swipe_start_pos.y())

            if (delta_x <= self.click_threshold and
                    delta_y <= self.click_threshold and
                    gesture_duration <= self.max_click_time):
                self.handle_click(self.swipe_start_pos)

        self.is_swiping = False
        self.swipe_start_pos = None
        self.reset_inactivity_timer()  # Сбрасываем таймер после жеста
        return False

    def handle_click(self, click_pos: QtCore.QPoint):
        """Обработка клика по элементу"""
        QtCore.QTimer.singleShot(50, lambda: self.process_click(click_pos))

    def process_click(self, click_pos: QtCore.QPoint):
        """Фактическая обработка клика после задержки"""
        content_pos = self.scroll_content.mapFromParent(click_pos)

        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.geometry().contains(content_pos):
                    if isinstance(widget, ProductsItemWidget):
                        self.item_clicked.emit(widget.guid)
                        """
                        item_data = self.find_item_data_by_guid(widget.guid)
                        if item_data:
                            self.item_clicked.emit(widget.guid, item_data)
                        """
                    break

        # Сбрасываем таймер после клика
        self.reset_inactivity_timer()

    def find_item_data_by_guid(self, guid: str) -> dict:
        for item in self.gallery_data.get("items", []):
            if item.get("guid") == guid:
                return item
        return {}

    def process_swipe_gesture(self, start_pos: QtCore.QPoint, current_pos: QtCore.QPoint, current_time: float):
        if not start_pos:
            return

        delta_y = current_pos.y() - start_pos.y()
        delta_time = current_time - self.last_time

        if delta_time > 0:
            instantaneous_velocity = delta_y / delta_time
            self.velocity = instantaneous_velocity * 0.7 + self.velocity * 0.3

        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()
        scrollbar.setValue(int(current_value - delta_y))

        self.last_pos = current_pos
        self.last_time = current_time

    def start_inertia(self):
        if abs(self.velocity) > 10:
            self.inertia_timer.start()

    def stop_inertia(self):
        self.inertia_timer.stop()
        self.velocity = 0

    def update_inertia(self):
        if abs(self.velocity) < 10:
            self.stop_inertia()
            return

        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()

        delta = self.velocity * 0.016

        if self.velocity > 0:
            self.velocity = max(0, self.velocity - 1000 * 0.016)
        else:
            self.velocity = min(0, self.velocity + 1000 * 0.016)

        new_value = current_value - delta

        if new_value < scrollbar.minimum():
            new_value = scrollbar.minimum()
            self.velocity = -self.velocity * 0.3
        elif new_value > scrollbar.maximum():
            new_value = scrollbar.maximum()
            self.velocity = -self.velocity * 0.3

        scrollbar.setValue(int(new_value))

    def smooth_scroll_to(self, target_value: int, duration: int = 500):
        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()

        self.animation = QPropertyAnimation(scrollbar, b"value")
        self.animation.setDuration(duration)
        self.animation.setStartValue(current_value)
        self.animation.setEndValue(target_value)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        #self.load_gallery_data()

    def calculate_item_size(self):
        gallery_width = self.width() - 40
        if gallery_width <= 0:
            gallery_width = 400

        image_width = int(gallery_width * self.settings.IMAGE_SIZE_PERCENT)
        image_height = image_width

        return QSize(image_width, image_height)

    def load_gallery_data(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        item_size = self.settings.ITEMS_LINE_SIZE

        for item_data in self.gallery_data:

            item_widget = ProductsItemWidget(
                item_data[2],
                item_data[1],
                item_data[0],
                item_data[3],
                item_data[4],
                item_size
            )
            self.scroll_layout.addWidget(item_widget)

        self.scroll_layout.addStretch()
        self.reset_inactivity_timer()  # Сбрасываем таймер после загрузки данных


class ItemPriceWidget(QWidget):
    itemClicked = pyqtSignal(str)
    def __init__(self, item_size, price, discount):
        super().__init__()
        self.price = price
        self.discount = discount
        self.item_size = item_size
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.price_label = QLabel(f"{self.price:.2f} ₽")
        self.price_label.setFixedWidth(300)
        layout.addWidget(self.price_label)
        if self.discount == 0 or self.discount == None:
            self.price_label.setObjectName("price_label")
        else:
            self.price_label.setObjectName("price_label_decor")
            self.price_discount_label = QLabel(f"{self.discount:.2f} ₽")
            self.price_discount_label.setObjectName("price_discount_label")
            self.price_discount_label.setFixedWidth(300)
            layout.addWidget(self.price_discount_label)
class ProductsItemWidget(QWidget):
    itemClicked = pyqtSignal(str)

    def __init__(self, guid: str, name: str, image_filename: str, price, discount, item_size):
        super().__init__()
        self.guid = guid
        self.name = name
        self.image_filename = image_filename
        self.price = price
        self.discount = discount
        self.item_size = item_size
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.image_label = ClickableLabel(self.guid)
        self.image_label.setFixedHeight(self.item_size)
        self.image_label.setFixedWidth(self.item_size * 2)
        self.image_label.setAlignment(Qt.AlignCenter)
        #self.image_label.setStyleSheet("border: 1px solid #333333; border-radius: 5px; background-color: #1a1a1a;")

        self.image_label.clicked.connect(self.itemClicked.emit)
        self.load_image()

        self.name_label = ClickableLabel(self.guid)
        self.name_label.setText(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(False)
        #self.name_label.setMaximumWidth(self.item_size.width())
        self.name_label.setObjectName("GaleryLabel")
        self.name_label.setStyleSheet(STYLES)
        self.name_label.clicked.connect(self.itemClicked.emit)

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        product_price = ItemPriceWidget(self.item_size, self.price, self.discount)
        layout.addWidget(product_price)




    def load_image(self):
        try:
            original_pixmap = QPixmap(Settings.PRODUCT_IMAGE_PATH + "\\" + self.image_filename)
            pixmap = original_pixmap.scaledToHeight(self.item_size, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

        except Exception as e:
            print(f"Ошибка загрузки изображения {self.image_filename}: {e}")
            pixmap = QPixmap(self.item_size, self.item_size)
            pixmap.fill(Qt.darkGray)
            self.image_label.setPixmap(pixmap)
