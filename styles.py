# Настройки цветовой схемы для темной темы
DARK_THEME = {
    # Основные цвета
    'BACKGROUND': '#000000',
    'BACKGROUND_SECONDARY': '#1a1a1a',
    'BACKGROUND_TERTIARY': '#2a2a2a',
    'BACKGROUND_DISCOUNT_DESCRIPTION': '#FFD700',
    'PAY_BUTTON': '#00FF00',
    'PAY_DISCOUNT_BUTTON': '#FF4500',

    # Цвета текста
    'TEXT_PRIMARY': '#ffffff',
    'TEXT_CONTRAST': '#000000',
    'TEXT_SECONDARY': '#cccccc',
    'TEXT_MUTED': '#999999',
    'TEXT_PRICE': '#00FF00',
    'TEXT_DISCOUNT_PRICE': '#FF4500',
    'TEXT_NAME_DESCRIPTION': '#FFA500',
    'TEXT_DISCOUNT_DESCRIPTION': '#000000',

    # Цвета границ
    'BORDER_PRIMARY': '#333333',
    'BORDER_SECONDARY': '#666666'
}


STYLES = f"""
/* Основные стили приложения */

QMainWindow {{
    background-color: {DARK_THEME['BACKGROUND']};
}}

QWidget {{
    background-color: {DARK_THEME['BACKGROUND']};
    color: {DARK_THEME['BACKGROUND']};
    border: None;
}}


QWidget#product_item {{
    background-color: #1a1a1a !important;
    color: #000000 !important;
    border: 1px solid #666666 !important;
}}

/* Стили для списка */
QPushButton {{
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
    background-color: transparent;
    font-size: 20px;
    color: {DARK_THEME['TEXT_PRIMARY']};
}}

/* Кнопка оплаты */
QPushButton#price_button {{
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
    border-radius: 10px;
    background-color: {DARK_THEME['PAY_BUTTON']};
    font-size: 30px;
    color: {DARK_THEME['TEXT_CONTRAST']};
}}

QPushButton#text_image_Button {{
    background-color: {DARK_THEME['BACKGROUND']};
    color: {DARK_THEME['BACKGROUND']};
    border: None;
}}

/* Кнопка оплаты со скидкой*/
QPushButton#discount_price_button {{
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
    border-radius: 10px;
    background-color: {DARK_THEME['PAY_DISCOUNT_BUTTON']};
    font-size: 30px;
    color: {DARK_THEME['TEXT_CONTRAST']};
}}

/* Стиль заголовка */
QLabel#title_label {{
    font-size: 50px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_PRIMARY']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};
    border: None;
}}

/* Описание продукта */
QLabel#product_description {{
    font-size: 30px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_PRIMARY']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};
}}


QLabel#remaining_time_label {{
    font-size: 30px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_PRIMARY']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};
}}

/* Описание скидки */
QLabel#discount_description {{
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
    border-radius: 10px;
    font-size: 25px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_DISCOUNT_DESCRIPTION']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND_DISCOUNT_DESCRIPTION']};
}}

/* Наименование параметра */
QLabel#description_name {{
    font-size: 20px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_NAME_DESCRIPTION']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND_SECONDARY']};
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
}}

/* Кнопка выбора способа оплаты */
QPushButton#payment_metod {{
                background-color: {DARK_THEME['BACKGROUND_SECONDARY']};
                color: {DARK_THEME['TEXT_PRIMARY']};
                border: none;
                padding: 20px 15px;
                border-radius: 10px;
                font-size: 14pt;
                font-weight: bold;
                min-height: 120px;
                min-width: 200px;
}}

/* Текст параметра */
QLabel#description_text {{
    font-size: 20px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_PRIMARY']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND_SECONDARY']};
    border: 1px solid {DARK_THEME['BORDER_SECONDARY']};
}}

/* Стиль цены */
QLabel#price_label {{
    font-size: 30px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_PRICE']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};
}}

QLabel#price_label_decor {{
    font-size: 30px;
    font-weight: bold;
    text-decoration: line-through;
    color: {DARK_THEME['TEXT_PRICE']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};
}}
    
QLabel#price_discount_label {{
    font-size: 30px;
    font-weight: bold;
    color: {DARK_THEME['TEXT_DISCOUNT_PRICE']};
    padding: 10px;
    background-color: {DARK_THEME['BACKGROUND']};

}}

#GaleryLabel {{
    background-color: {DARK_THEME['BACKGROUND']};
    color: {DARK_THEME['TEXT_PRIMARY']};
    border: None;
    font-weight: bold;
    font-size: 30px;
}}
"""
