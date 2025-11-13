from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QScrollArea,
                             QSizePolicy, QScroller, QScrollerProperties, QMessageBox)
from PyQt5.QtGui import QPixmap, QMouseEvent, QKeyEvent, QPainter, QIcon, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QEvent, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5 import QtCore, QtWidgets

from styles import STYLES
from settings import Settings
import time

class TextImageButton(QPushButton):
    def __init__(self, text: str, file_name: str, parent=None):
        super().__init__(text, parent)
        self.image_path = file_name
        self.original_pixmap = None
        self.setStyleSheet(STYLES)
        self.original_pixmap = QPixmap(self.image_path)
        self.setObjectName("text_image_Button")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_icon()

    def update_icon(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            target_height = self.height()
            if target_height > 0:
                scaled_pixmap = self.original_pixmap.scaledToHeight(
                    target_height,
                    Qt.SmoothTransformation
                )
                self.setIcon(QIcon(scaled_pixmap))
                self.setIconSize(scaled_pixmap.size())
                self.setFixedWidth(scaled_pixmap.width())


class TopPanel (QWidget):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setStyleSheet(STYLES)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(self.settings.TOP_PANEL_HEIGHT)
        self.setObjectName("topPanel")
        self.setStyleSheet(STYLES)

        top_layout = QHBoxLayout(self)
        top_layout.setContentsMargins(
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING
        )
        top_layout.setSpacing(10)

        self.home_button = TextImageButton("", Settings.ICONS_PATH + "\\home.png")  # В начало
        self.home_button.setFixedHeight(self.settings.TOP_PANEL_HEIGHT - 20)
        self.home_button.setFixedWidth(self.settings.TOP_PANEL_HEIGHT - 20)

        self.back_button = TextImageButton("", Settings.ICONS_PATH + "\\back.png")  # В начало
        self.back_button.setFixedHeight(self.settings.TOP_PANEL_HEIGHT - 20)
        self.back_button.setFixedWidth(self.settings.TOP_PANEL_HEIGHT - 20)

        self.title_label = QLabel("Заголовок окна")
        self.title_label.setObjectName("title_label")
        self.title_label.setStyleSheet(STYLES)

        top_layout.addWidget(self.home_button)
        top_layout.addWidget(self.back_button)
        top_layout.addStretch()
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()


class BottomPanel (QWidget):

    discount_btn = False

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setStyleSheet(STYLES)
        self.setup_ui()
    def setup_ui(self):
        self.setFixedHeight(self.settings.BOTTOM_PANEL_HEIGHT)
        self.setObjectName("topPanel")
        self.setStyleSheet(STYLES)

        top_layout = QHBoxLayout(self)
        top_layout.setContentsMargins(
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING,
            self.settings.PANEL_PADDING
        )
        top_layout.setSpacing(10)


        self.logo_button = TextImageButton("", Settings.ICONS_PATH + "\\logo.png")  # Лого
        self.logo_button.setFixedHeight(self.settings.BOTTOM_PANEL_HEIGHT - 20)
        self.logo_button.setFixedWidth(self.settings.LOGO_WIDTH - 20)


        self.discount_button = TextImageButton("", Settings.ICONS_PATH + "\\discount.png")  # Системное меню
        self.discount_button.setFixedHeight(self.settings.BOTTOM_PANEL_HEIGHT - 20)
        self.discount_button.setFixedWidth(self.width() - self.settings.LOGO_WIDTH - self.settings.BOTTOM_PANEL_HEIGHT - 80)

        self.system_button = TextImageButton("", Settings.ICONS_PATH + "\\settings.png")  # Системное меню
        self.system_button.setFixedHeight(self.settings.BOTTOM_PANEL_HEIGHT - 20)
        self.system_button.setFixedWidth(self.settings.BOTTOM_PANEL_HEIGHT - 20)

        top_layout.addWidget(self.logo_button)
        top_layout.addStretch()
        top_layout.addWidget(self.discount_button)
        top_layout.addStretch()
        top_layout.addWidget(self.system_button)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.discount_button.setFixedWidth(self.width() - self.settings.LOGO_WIDTH - self.settings.BOTTOM_PANEL_HEIGHT - 80)




class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, guid=None):
        super().__init__()
        self.guid = guid
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.guid:
            self.clicked.emit(self.guid)
        super().mousePressEvent(event)


class AdvancedMarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._position = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_position)
        self._speed = 3
        self._text_width = 0
        self._is_animating = False
        self._direction = -1  # -1 для движения слева направо, 1 для справа налево
        self._gap = 50  # Расстояние между повторениями текста

        self.setMinimumHeight(60)
        self.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2b2b2b, stop:0.5 #3a3a3a, stop:1 #2b2b2b);
                color: #00ff00;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                border: 2px solid #00ff00;
                font-family: 'Arial';
            }
        """)

    def _update_position(self):
        if not self._is_animating:
            return

        self._position += self._speed * self._direction

        # Сбрасываем позицию когда текст полностью уходит
        if self._direction == -1 and self._position < -self._text_width:
            self._position = self.width()
        elif self._direction == 1 and self._position > self.width():
            self._position = -self._text_width

        self.update()

    def paintEvent(self, event):
        # Рисуем стандартный фон
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.setFont(self.font())

        # Получаем размеры текста
        self._text_width = self.fontMetrics().width(self.text())
        text_height = self.fontMetrics().height()

        # Вычисляем вертикальную позицию для центрирования
        y_pos = (self.height() - text_height) / 2 + text_height - 2

        # Рисуем несколько копий текста для плавного перехода
        x = self._position
        while x < self.width() + self._text_width:
            painter.drawText(int(x), int(y_pos), self.text())
            x += self._text_width + self._gap

    def start_animation(self):
        self._is_animating = True
        self._position = self.width() if self._direction == -1 else -self._text_width
        self._timer.start(30)

    def stop_animation(self):
        self._is_animating = False
        self._timer.stop()

    def set_speed(self, speed):
        self._speed = max(1, min(20, speed))  # Ограничиваем скорость

    def set_direction(self, direction):
        """Установка направления: -1 слева направо, 1 справа налево"""
        self._direction = direction

    def toggle_direction(self):
        self._direction *= -1