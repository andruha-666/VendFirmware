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

class ScrollPanel(QWidget):
    gallery_data = {}
    root_menu = True
    item_clicked = pyqtSignal(str, dict)  # guid, item_data

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setStyleSheet(STYLES)
        self.setup_ui()
        self.setup_swipe_gestures()
        self.setup_animation()
        self.setup_inactivity_timer()

    def setup_ui(self):
        self.gallery_layout = QVBoxLayout(self)
        self.gallery_layout.setContentsMargins(0, 0, 0, 0)
        self.gallery_layout.setSpacing(0)

        # Создаем QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Создаем контент для скролла
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)

        # Устанавливаем контент в скролл
        self.scroll_area.setWidget(self.scroll_content)

        # Добавляем скролл в основной layout
        self.gallery_layout.addWidget(self.scroll_area)


    def setup_inactivity_timer(self):
        """Настройка таймера бездействия для автоматической прокрутки"""
        self.inactivity_timer = QTimer()
        self.inactivity_timer.setSingleShot(True)
        self.inactivity_timer.timeout.connect(self.start_auto_scroll)
        self.reset_inactivity_timer()

    def reset_inactivity_timer(self):
        """Сброс таймера бездействия"""
        # if self.root_menu:  # Только для корневого меню
        #    self.inactivity_timer.start(self.settings.INACTIVITY_TIMEOUT * 1000)
        self.inactivity_timer.start(self.settings.INACTIVITY_TIMEOUT * 1000)

    def stop_inactivity_timer(self):
        self.inactivity_timer.stop()

    def reset_inactivity_timer_from_scroll(self):
        """Сброс таймера бездействия"""
        if self.root_menu:  # Только для корневого меню
            self.inactivity_timer.start(500)

    def start_auto_scroll(self):
        """Запуск автоматической прокрутки при бездействии"""
        if not self.root_menu or not self.scroll_area or not self.scroll_content:
            # Если не корневое меню - эмитируем событие клика с None
            if not self.root_menu:
                print("Таймер бездействия в не корневом меню - эмитируем клик с None")
                self.item_clicked.emit(None, {})
            return

        scrollbar = self.scroll_area.horizontalScrollBar()
        if not scrollbar.isVisible() or scrollbar.maximum() <= 0:
            # Если прокрутка не нужна, перезапускаем таймер
            self.reset_inactivity_timer()
            return

        # Определяем направление прокрутки
        current_value = scrollbar.value()
        if current_value >= scrollbar.maximum():
            # Достигли конца - прокручиваем к началу
            target_value = scrollbar.minimum()
        else:
            # Прокручиваем вперед
            #target_value = min(scrollbar.maximum(), current_value + 400)
            target_value = scrollbar.maximum()

        # Плавная прокрутка
        self.smooth_scroll_to(target_value, 1000)  # 1 секунда на анимацию

        # Перезапускаем таймер для следующей прокрутки
        QTimer.singleShot(1200, self.reset_inactivity_timer_from_scroll)  # Ждем окончания анимации + задержка

    def setup_swipe_gestures(self):
        """Настройка жестов свайпа"""
        self.scroll_area.setAttribute(Qt.WA_AcceptTouchEvents)
        self.scroll_content.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setAttribute(Qt.WA_AcceptTouchEvents)

        # Переменные для отслеживания свайпа
        self.swipe_start_pos = None
        self.swipe_start_time = None
        self.last_pos = None
        self.last_time = None
        self.velocity = 0
        self.is_swiping = False
        self.click_threshold = 10  # Максимальное перемещение для определения клика

        # Параметры свайпа
        self.swipe_threshold = 30
        self.deceleration = 1000
        self.min_velocity = 10

    def setup_animation(self):
        """Настройка анимации инерции"""
        self.inertia_timer = QTimer()
        self.inertia_timer.timeout.connect(self.update_inertia)
        self.inertia_timer.setInterval(16)

    def event(self, event: QEvent) -> bool:
        """Обработка событий жестов с сбросом таймера бездействия"""
        # Сначала обрабатываем жесты
        if event.type() == QEvent.TouchBegin:
            result = self.handle_touch_begin(event)
        elif event.type() == QEvent.TouchUpdate:
            result = self.handle_touch_update(event)
        elif event.type() == QEvent.TouchEnd:
            result = self.handle_touch_end(event)
        elif event.type() == QEvent.MouseButtonPress:
            result = self.handle_mouse_press(event)
        elif event.type() == QEvent.MouseMove:
            result = self.handle_mouse_move(event)
        elif event.type() == QEvent.MouseButtonRelease:
            result = self.handle_mouse_release(event)
        else:
            result = super().event(event)

        # Сбрасываем таймер бездействия при любом пользовательском взаимодействии
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove,
                            QEvent.MouseButtonRelease, QEvent.TouchBegin,
                            QEvent.TouchUpdate, QEvent.TouchEnd]:
            self.reset_inactivity_timer()
            self.stop_auto_scroll()

        return result

    def stop_auto_scroll(self):
        """Остановка автоматической прокрутки"""
        if hasattr(self, 'animation') and self.animation:
            self.animation.stop()

    def handle_touch_begin(self, event: QEvent) -> bool:
        """Обработка начала касания"""
        if event.touchPoints():
            self.stop_inertia()
            self.stop_auto_scroll()
            self.swipe_start_pos = event.touchPoints()[0].pos()
            self.swipe_start_time = time.time()
            self.last_pos = self.swipe_start_pos
            self.last_time = self.swipe_start_time
            self.is_swiping = False  # Пока не знаем, это свайп или клик
            return True
        return False

    def handle_touch_update(self, event: QEvent) -> bool:
        """Обработка движения касания"""
        if not self.swipe_start_pos or not event.touchPoints():
            return False

        current_pos = event.touchPoints()[0].pos()
        current_time = time.time()

        # Проверяем, превысили ли порог для свайпа
        delta_x = abs(current_pos.x() - self.swipe_start_pos.x())
        delta_y = abs(current_pos.y() - self.swipe_start_pos.y())

        if delta_x > self.click_threshold or delta_y > self.click_threshold:
            # Превысили порог - это свайп
            self.is_swiping = True
            self.process_swipe_gesture(self.last_pos, current_pos, current_time)

        self.last_pos = current_pos
        self.last_time = current_time
        return True

    def handle_touch_end(self, event: QEvent) -> bool:
        """Обработка окончания касания"""
        if not self.swipe_start_pos:
            return True

        # Если это был свайп - запускаем инерцию
        if self.is_swiping and self.velocity != 0:
            self.start_inertia()
        else:
            # Если не было свайпа - это клик
            self.handle_click(self.swipe_start_pos)

        self.is_swiping = False
        self.swipe_start_pos = None
        return True

    def handle_mouse_press(self, event: QMouseEvent) -> bool:
        """Обработка нажатия мыши (для тестирования)"""
        if event.button() == Qt.LeftButton:
            self.stop_inertia()
            self.stop_auto_scroll()
            self.swipe_start_pos = event.pos()
            self.swipe_start_time = time.time()
            self.last_pos = self.swipe_start_pos
            self.last_time = self.swipe_start_time
            self.is_swiping = False
            return True
        return False

    def handle_mouse_move(self, event: QMouseEvent) -> bool:
        """Обработка движения мыши с зажатой кнопкой"""
        if self.swipe_start_pos and event.buttons() & Qt.LeftButton:
            current_pos = event.pos()
            current_time = time.time()

            # Проверяем порог для определения свайпа
            delta_x = abs(current_pos.x() - self.swipe_start_pos.x())
            delta_y = abs(current_pos.y() - self.swipe_start_pos.y())

            if delta_x > self.click_threshold or delta_y > self.click_threshold:
                # Превысили порог - это свайп
                self.is_swiping = True
                self.process_swipe_gesture(self.last_pos, current_pos, current_time)

            self.last_pos = current_pos
            self.last_time = current_time
            return True
        return False

    def handle_mouse_release(self, event: QMouseEvent) -> bool:
        """Обработка отпускания кнопки мыши"""
        if not self.swipe_start_pos:
            return False

        # Если это был свайп - запускаем инерцию
        if self.is_swiping and self.velocity != 0:
            self.start_inertia()
        else:
            # Если не было свайпа - это клик
            self.handle_click(self.swipe_start_pos)

        self.is_swiping = False
        self.swipe_start_pos = None
        return False

    def handle_click(self, click_pos: QtCore.QPoint):
        """Обработка клика по элементу"""
        content_pos = self.scroll_content.mapFromParent(click_pos)
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.geometry().contains(content_pos):
                    if isinstance(widget, GalleryItemWidget):
                        # Находим данные элемента в gallery_data
                        item_data = self.find_item_data_by_guid(widget.guid)
                        if item_data:
                            # Эмитируем сигнал с данными элемента
                            self.item_clicked.emit(widget.guid, item_data)
                        break

    def find_item_data_by_guid(self, guid: str) -> dict:
        """Находит данные элемента по GUID"""
        for item in self.gallery_data.get("items", []):
            if item.get("guid") == guid:
                return item
        return {}

    def process_swipe_gesture(self, start_pos: QtCore.QPoint, current_pos: QtCore.QPoint, current_time: float):
        """Обработка жеста свайпа с вычислением скорости"""
        if not start_pos:
            return

        # Вычисляем разницу в координатах и времени
        delta_x = current_pos.x() - start_pos.x()
        delta_time = current_time - self.last_time

        if delta_time > 0:
            # Вычисляем мгновенную скорость
            instantaneous_velocity = delta_x / delta_time
            # Сглаживаем скорость
            self.velocity = instantaneous_velocity * 0.7 + self.velocity * 0.3

        # Прокручиваем содержимое
        scrollbar = self.scroll_area.horizontalScrollBar()
        current_value = scrollbar.value()
        scrollbar.setValue(int(current_value - delta_x))

    def start_inertia(self):
        """Запуск анимации инерции"""
        if abs(self.velocity) > self.min_velocity:
            self.inertia_timer.start()

    def stop_inertia(self):
        """Остановка анимации инерции"""
        self.inertia_timer.stop()
        self.velocity = 0

    def update_inertia(self):
        """Обновление анимации инерции"""
        if abs(self.velocity) < self.min_velocity:
            self.stop_inertia()
            return

        # Применяем инерцию
        scrollbar = self.scroll_area.horizontalScrollBar()
        current_value = scrollbar.value()

        # Вычисляем смещение на основе скорости
        delta = self.velocity * 0.016  # 16ms = 0.016s

        # Применяем замедление
        if self.velocity > 0:
            self.velocity = max(0, self.velocity - self.deceleration * 0.016)
        else:
            self.velocity = min(0, self.velocity + self.deceleration * 0.016)

        # Прокручиваем с инерцией
        new_value = current_value - delta

        # Проверяем границы
        if new_value < scrollbar.minimum():
            new_value = scrollbar.minimum()
            self.velocity = -self.velocity * 0.3  # Отскок от границы
        elif new_value > scrollbar.maximum():
            new_value = scrollbar.maximum()
            self.velocity = -self.velocity * 0.3  # Отскок от границы

        scrollbar.setValue(int(new_value))

    def smooth_scroll_to(self, target_value: int, duration: int = 500):
        """Плавная прокрутка к указанной позиции"""
        scrollbar = self.scroll_area.horizontalScrollBar()
        current_value = scrollbar.value()

        self.animation = QPropertyAnimation(scrollbar, b"value")
        self.animation.setDuration(duration)
        self.animation.setStartValue(current_value)
        self.animation.setEndValue(target_value)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def update_existing_items(self):
        """Обновляет размеры существующих элементов без пересоздания"""
        item_size = self.calculate_item_size()
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), GalleryItemWidget):
                widget = item.widget()
                widget.item_size = item_size
                widget.image_label.setFixedSize(item_size)
                widget.name_label.setFixedWidth(item_size.width())
                widget.load_image()  # Перезагружаем изображение с новым размером

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_existing_items()
        #self.load_gallery_data()

    def calculate_item_size(self):
        gallery_height = self.height() - 40
        if gallery_height <= 0:
            gallery_height = 400

        image_height = int(gallery_height * self.settings.IMAGE_SIZE_PERCENT)
        image_width = image_height

        return QSize(image_width, image_height)

    def load_gallery_data(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        item_size = self.calculate_item_size()

        for item_data in self.gallery_data.get("items", []):
            item_widget = GalleryItemWidget(
                item_data["guid"],
                item_data["name"],
                item_data["image"],
                item_size
            )
            # Подключаем сигнал клика по элементу
            #item_widget.itemClicked.connect(self.on_gallery_item_clicked)
            self.scroll_layout.addWidget(item_widget)

        self.scroll_layout.addStretch()
        self.reset_inactivity_timer()

    #def on_gallery_item_clicked(self, guid: str):
        """Обработчик клика по элементу галереи"""
        #print(f"Элемент галереи clicked: {guid}")
        # Здесь можно добавить логику перехода к подкатегории или товару

class GalleryItemWidget(QWidget):
    itemClicked = pyqtSignal(str)

    def __init__(self, guid: str, name: str, image_filename: str, item_size: QSize):
        super().__init__()
        self.guid = guid
        self.name = name
        self.image_filename = image_filename
        self.item_size = item_size
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.image_label = ClickableLabel(self.guid)
        self.image_label.setFixedSize(self.item_size)
        self.image_label.setAlignment(Qt.AlignCenter)
        #self.image_label.setStyleSheet("border: 1px solid #333333; border-radius: 5px; background-color: #1a1a1a;")

        self.image_label.clicked.connect(self.itemClicked.emit)
        self.load_image()

        self.name_label = ClickableLabel(self.guid)
        self.name_label.setText(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumWidth(self.item_size.width())
        self.name_label.setObjectName("GaleryLabel")
        self.name_label.setStyleSheet(STYLES)
        self.name_label.clicked.connect(self.itemClicked.emit)

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)
        layout.addStretch()

    def load_image(self):
        try:
            original_pixmap = QPixmap(Settings.CATEGORY_IMAGE_PATH + "\\" + self.image_filename)
            pixmap = original_pixmap.scaledToHeight(self.item_size.height(), Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

        except Exception as e:
            print(f"Ошибка загрузки изображения {self.image_filename}: {e}")
            pixmap = QPixmap(self.item_size)
            pixmap.fill(Qt.darkGray)
            self.image_label.setPixmap(pixmap)



