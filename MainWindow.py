# pip install screeninfo

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSizePolicy)
from settings import Settings
from styles import STYLES
from visual_elements import TopPanel,  BottomPanel
from scroll_panel import ScrollPanel
from vertical_scroll_panel import VerticalScrollPanel
from database import Database
from constants import Constants as const
from product_description import ProductDescription
from screeninfo import get_monitors
from payment_metods import PaymentMetods

class MainWindow(QMainWindow):
    previous_status = const.ST_WAIT
    display_height = None
    display_width = None
    visible_item = None

    def __init__(self):
        super().__init__()

        self.db = Database()
        self.root_menu = True
        self.category_guid = None
        self.product_guid = None
        self.product_price = None
        self.workflow_step = const.ST_WAIT
        self.settings = Settings()
        self.setStyleSheet(STYLES)
        for monitor in get_monitors():
            if monitor.is_primary:
                print(f"Primary display {monitor.name}, height {monitor.height}, width {monitor.width}")
                self.display_height = monitor.height
                self.display_width = monitor.width

        self.setup_ui()
        self.workflow(const.GO_HOME, None)
        #self.workflow(const.GO_PAYMENT_METODS, None)


    def enableInactiveTimer(self, item_panel):
        self.galery.stop_inactivity_timer()
        self.products.stop_inactivity_timer()
        self.product_description.stop_inactivity_timer()
        match item_panel:
            case const.ITEM_CATEGORY:
                self.galery.reset_inactivity_timer()
            case const.ITEM_PRODUCTS_LIST:
                self.products.reset_inactivity_timer()
            case const.ITEM_PRODUCT_DETAILS:
                self.product_description.reset_inactivity_timer()
            case const.PAYMET_METODS:
                self.payment_metods.setup_inactivity_timer()


    def setVisibleItems(self, navigation_panel, bottom_panel, item_panel):
        self.top_panel.setVisible(navigation_panel)
        self.bottom_panel.setVisible(bottom_panel)
        if item_panel == const.ITEM_CATEGORY:
            self.top_panel.title_label.setText("Выберите категорию")
            self.galery.setVisible(True)
        else:
            self.galery.setVisible(False)
        if item_panel == const.ITEM_PRODUCTS_LIST:
            self.top_panel.title_label.setText("Выберите блюдо")
            self.products.setVisible(True)
        else:
            self.products.setVisible(False)
        if item_panel == const.ITEM_PRODUCT_DETAILS:
            self.top_panel.title_label.setText("Наименование блюда")
            self.product_description.setVisible(True)
        else:
            self.product_description.setVisible(False)
        if item_panel == const.PAYMET_METODS:
            self.top_panel.title_label.setText("Выберите способ оплаты")
            self.payment_metods.setVisible(True)
        else:
            self.payment_metods.setVisible(False)
        self.visible_item = item_panel
        self.enableInactiveTimer(item_panel)

    def workflow(self, step, guid):
        match step:
            case const.GO_HOME:
                self.load_category(None)
                self.category_guid = None
                self.setVisibleItems(True, True, const.ITEM_CATEGORY)
                self.top_panel.home_button.setEnabled(False)
                self.top_panel.back_button.setEnabled(False)
                self.workflow_step = const.ST_WAIT

            case const.GO_PRODUCTS_LIST:
                self.load_products(guid)
                self.setVisibleItems(True, False, const.ITEM_PRODUCTS_LIST)
                self.top_panel.home_button.setEnabled(True)
                self.top_panel.back_button.setEnabled(True)
                self.workflow_step = const.ST_PRODUCT_LIST

            case const.GO_SUBCATEGORY:
                if guid is None:
                    self.workflow(const.GO_HOME, None)
                else:
                    self.load_category(guid)
                    self.setVisibleItems(True, False, const.ITEM_CATEGORY)
                    self.top_panel.home_button.setEnabled(True)
                    self.top_panel.back_button.setEnabled(True)
                    self.workflow_step = const.ST_SUBCATEGORY

            case const.GO_BACK:
                match self.workflow_step:
                    case const.ST_PRODUCT_LIST:
                        self.workflow(const.GO_SUBCATEGORY, self.category_guid)
                    case const.ST_SUBCATEGORY:
                        self.workflow(const.GO_SUBCATEGORY, self.db.get_parent_category(self.category_guid))
                    case const.ST_PRODUCT_DETAILS:
                        self.workflow(const.GO_PRODUCTS_LIST, self.category_guid)
                    case const.ST_PAYMET_METODS:
                        self.workflow(const.GO_PRODUCT_DETAILS, self.product_guid)

            case const.GO_PRODUCT_DETAILS:
                if guid:
                    self.setVisibleItems(True, False, const.ITEM_PRODUCT_DETAILS)
                    data = self.db.get_product_by_id(guid)
                    self.product_description.load_data(data)
                    self.top_panel.title_label.setText(data["name"])
                    self.top_panel.home_button.setEnabled(True)
                    self.top_panel.back_button.setEnabled(True)
                    self.workflow_step = const.ST_PRODUCT_DETAILS

            case const.GO_PAYMENT_METODS:
                self.payment_metods.set_price(self.product_price)
                self.setVisibleItems(True, False, const.PAYMET_METODS)
                self.top_panel.home_button.setEnabled(True)
                self.top_panel.back_button.setEnabled(True)
                self.workflow_step = const.ST_PAYMET_METODS

    def load_category(self, guid):
        data = self.db.get_categories_with_products_hierarchy(guid)
        if len(data['items']) != 0:
            self.galery.gallery_data = data
            self.galery.load_gallery_data()
            self.category_guid = guid

    def load_products(self, guid):
        data = self.db.get_items_by_category(guid)
        if len(data) != 0:
            self.products.gallery_data = data
            self.products.load_gallery_data()

    def on_click_buttons(self, tmp):
        self.workflow(tmp, None)

    def on_scroll_item_clicked(self, guid: str, item_data: dict):
        if guid is None:
            self.workflow(const.GO_HOME, None)
        else:
            if self.db.subcategories(guid) == 0:
                self.workflow(const.GO_PRODUCTS_LIST, guid)
            else:
                self.workflow(const.GO_SUBCATEGORY, guid)

    def on_product_clicked(self, guid: str):
        if guid is None or guid == "":
            self.workflow(const.GO_HOME, None)
        else:
            self.product_guid = guid
            self.workflow(const.GO_PRODUCT_DETAILS, guid)

    def on_pay_clicked(self, price: float):
        if price is None:
            self.payment_metods.price = None
            self.workflow(const.GO_HOME, None)
        else:
            self.product_price = price
            self.workflow(const.GO_PAYMENT_METODS, None)

    def on_payment_metod(self, metod: str):
        ############# Добавить обработку платежа  #############
        self.workflow(const.GO_HOME, None)
        
    def setup_ui(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.display_width, self.display_height)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.top_panel = TopPanel()
        self.bottom_panel = BottomPanel()
        self.galery = ScrollPanel()
        self.products = VerticalScrollPanel()
        self.product_description = ProductDescription()
        self.payment_metods = PaymentMetods(self.db.get_payments_metods())

        self.galery.root_menu = True
        self.galery.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.top_panel.home_button.clicked.connect(lambda: self.workflow(const.GO_HOME, None))
        self.top_panel.back_button.clicked.connect(lambda: self.workflow(const.GO_BACK, None))
        self.bottom_panel.logo_button.clicked.connect(lambda: self.on_click_buttons(const.GO_LOGO))
        self.bottom_panel.discount_button.clicked.connect(lambda: self.on_click_buttons(const.GO_DISCONT))
        self.bottom_panel.system_button.clicked.connect(lambda: self.on_click_buttons(const.GO_SYSTEM))
        self.galery.item_clicked.connect(self.on_scroll_item_clicked)
        self.products.item_clicked.connect(self.on_product_clicked)
        self.product_description.closed_with_result.connect(self.on_pay_clicked)
        self.payment_metods.closed_with_result.connect(self.on_payment_metod)

        self.main_layout.addWidget(self.top_panel)
        self.main_layout.addWidget(self.galery)
        self.galery.setVisible(False)
        self.main_layout.addWidget(self.products)
        self.products.setVisible(False)
        self.main_layout.addWidget(self.product_description)
        self.product_description.setVisible(False)
        self.main_layout.addWidget(self.payment_metods)
        self.payment_metods.setVisible(True)
        self.main_layout.addWidget(self.bottom_panel)


    def resizeEvent(self, event):
        super().resizeEvent(event)