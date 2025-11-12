import os


class Settings:
    # Высота панелей
    TOP_PANEL_HEIGHT = 150
    BOTTOM_PANEL_HEIGHT = 150
    LOGO_WIDTH = 300
    # Отступы для панелей
    PANEL_PADDING = 10
    ITEMS_LINE_SIZE = 150

    # Папка с иконками
    ICONS_PATH = "images\\icons"

    # Папка с изображениями категорий
    CATEGORY_IMAGE_PATH = "images\\categories"
    PRODUCT_IMAGE_PATH = "images\\products"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')

    # Размер картинки в процентах от области галереи (0.0 - 1.0)
    IMAGE_SIZE_PERCENT = 0.8  # 80% от высоты области галереи

    # Таймаут бездействия в секундах
    INACTIVITY_TIMEOUT = 10

    PAY_BUTTON_HEIGHT = 100
