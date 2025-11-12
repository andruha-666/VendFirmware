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