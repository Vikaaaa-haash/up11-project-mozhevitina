import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'logic')) 
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox
)
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from discount import calculate_price

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_card(product):
    # ИНДЕКСЫ (согласно нашему запросу в database.py):
    # 0:id, 1:category, 2:subcategory, 3:image, 4:name, 5:production, 
    # 6:description, 7:composition, 8:price, 9:stock, 10:discount_percent
    
    p_id = product[0]
    category = product[1]
    subcategory = product[2]
    image_name = product[3]
    name = product[4]
    production = product[5]
    description = product[6]
    composition = product[7]
    price = product[8]
    
    # Остаток
    try:
        stock = int(product[9]) if len(product) > 9 and product[9] is not None else 0
    except (ValueError, TypeError):
        stock = 0

    # Скидка из базы
    try:
        discount_percent = int(product[10]) if len(product) > 10 and product[10] is not None else 0
    except (ValueError, TypeError):
        discount_percent = 0

    # Считаем новую цену на основе скидки из БД
    old_price = float(price)
    new_price = old_price - (old_price * discount_percent / 100)

    # Картинка
    if image_name and str(image_name).strip() != "":
        image_path = f"resources/{image_name}"
    else:
        image_path = None

    if image_path and os.path.exists(image_path):
        pixmap = QPixmap(image_path)
    else:
        if image_name:
            logging.warning(f"Файл не найден: {image_name}. Использована заглушка.")
        pixmap = QPixmap("resources/picture.png")

    # Подсветка фона: если остаток меньше 3, красим в красный
    try:
        is_low_stock = int(stock) < 3
    except (ValueError, TypeError):
        is_low_stock = True
        
    bg_color = "#FF8080" if is_low_stock else "#FFFFFF"

    # Создание карточки
        # Создание карточки
    card = QWidget()
    # ВОЗВРАЩАЕМ СТИЛИ (без objectName, просто для HoverWidget)
    card = QWidget()
    card.setStyleSheet(f"""
        QWidget {{
            background-color: {bg_color};
            border: 1px solid #70B2AF;
            border-radius: 5px;
        }}
    """)
    card.setMinimumHeight(120) # Чтобы карточки не сплющивались
    main_layout = QHBoxLayout()
    # Даем нормальные отступы со всех сторон
    main_layout.setContentsMargins(15, 15, 15, 15)
    
    # Картинка
    image_label = QLabel()
    image_label.setFixedSize(100, 100)
    image_label.setAlignment(Qt.AlignCenter)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        image_label.setText("[НЕТ ФОТО]")
    main_layout.addWidget(image_label)
    
    # Текстовая часть
    text_layout = QVBoxLayout()
    text_layout.setAlignment(Qt.AlignTop) # Прижимаем текст к верху, чтобы он не расползался
    text_layout.setSpacing(5)
    
    title = QLabel(f"{production} | {name}")
    title.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; border: none;")
    text_layout.addWidget(title)
    
    cat_label = QLabel(f"Категория: {category}")
    cat_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(cat_label)
    
    comp_label = QLabel(f"Состав: {composition}")
    comp_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(comp_label)
    
    stock_label = QLabel(f"В наличии: {stock} шт.")
    text_color = "#8B0000" if is_low_stock else "#555555"
    stock_label.setStyleSheet(f"color: {text_color}; font-weight: bold; border: none;")
    text_layout.addWidget(stock_label)
    
    main_layout.addLayout(text_layout)
    
    # БЛОК С ЦЕНАМИ
    price_layout = QVBoxLayout()
    price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    price_layout.setContentsMargins(0, 0, 0, 0)

    # 1. СТАРАЯ ЦЕНА (Перечеркнутая и красная)
    old_price_label = QLabel(f"<s>{int(old_price)} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 14px; border: none;")
    old_price_label.setAlignment(Qt.AlignRight)
    price_layout.addWidget(old_price_label)

    # 2. Скрываем старую цену, если скидки нет
    if discount_percent > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    # 3. ИТОГОВАЯ ЦЕНА (Черная, жирная, с процентом скидки)
    if discount_percent > 0:
        new_price_label = QLabel(f"<nobr>{int(new_price)} ₽ <span style='color: #2E8B57; font-size: 14px;'>(-{discount_percent}%)</span></nobr>")
    else:
        new_price_label = QLabel(f"{int(new_price)} ₽")
        
    new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 18px; border: none;")
    new_price_label.setAlignment(Qt.AlignRight)
    price_layout.addWidget(new_price_label)

    # Просто добавляем layout с ценами в конец
    main_layout.addLayout(price_layout)
    card.setLayout(main_layout)

    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # --- АНИМАЦИЯ ПРИ НАВЕДЕНИИ (РАБОТАЕТ БЕЗ ГЛЮКОВ) ---
    effect = QGraphicsOpacityEffect(card)
    card.setGraphicsEffect(effect)
    
    card.anim = QPropertyAnimation(effect, b"opacity")
    card.anim.setDuration(200)
    
    def enter_event(event):
        card.anim.setStartValue(1.0)
        card.anim.setEndValue(0.9) # Делаем прозрачность чуть меньше, чтобы не было резко
        card.anim.start()
        QWidget.enterEvent(card, event)
        
    def leave_event(event):
        card.anim.setStartValue(0.9)
        card.anim.setEndValue(1.0)
        card.anim.start()
        QWidget.leaveEvent(card, event)

    card.enterEvent = enter_event
    card.leaveEvent = leave_event
    # ----------------------------------------------------


    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name
        self.db = Database()
        
        self.setWindowTitle("Ювелирный — Каталог")
        self.resize(900, 700)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        # --- HEADER ---
        top_layout = QHBoxLayout()
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(logo)
        
        title = QLabel("Ювелирный магазин")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF; margin-left: 10px;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()

        # ФИО и Роль (ДЗ из пары 37)
        if self.full_name:
            self.icon_label = QLabel()
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation)
            self.icon_label.setPixmap(icon.pixmap(24, 24))
            top_layout.addWidget(self.icon_label)

            self.fio_label = QLabel(f"{self.full_name} ({self.role_id})")
            self.fio_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-right: 15px; margin-left: 5px;")
            top_layout.addWidget(self.fio_label)

        # Кнопки ролей
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        top_layout.addWidget(self.order_button)
        top_layout.addWidget(self.manager_button)
        top_layout.addWidget(self.admin_button)

        # Кнопка Выход
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #FF8080; color: white; font-weight: bold; padding: 5px 15px;")
        self.logout_button.clicked.connect(self.logout)
        top_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(top_layout)

        # --- КАТАЛОГ (С СОРТИРОВКОЙ ПО СКИДКЕ) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        catalog_container = QWidget()
        catalog_layout = QVBoxLayout()
        catalog_layout.setSpacing(10) # Отступ между карточками
        catalog_layout.setAlignment(Qt.AlignTop)
        catalog_container.setLayout(catalog_layout)
        
        products = self.db.get_products()
        
        # Сортируем по размеру скидки (по убыванию), чтобы самые выгодные были сверху
        def get_discount(p):
            try:
                return int(p[10]) if len(p) > 10 and p[10] is not None else 0
            except:
                return 0
                
        products.sort(key=get_discount, reverse=True)
        
        for product in products:
            card = create_card(product)
            catalog_layout.addWidget(card)
            
        catalog_layout.addStretch()
        scroll.setWidget(catalog_container)
        main_layout.addWidget(scroll)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QScrollArea { border: none; background-color: #FFFFFF; }
            QWidget { background-color: #FFFFFF; }
            QLabel { border: none; }
        """)

    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        
        if self.role_id == "Клиент":
            self.order_button.show()
        elif self.role_id == "Менеджер":
            self.order_button.show()
            self.manager_button.show()
        elif self.role_id == "Администратор":
            self.order_button.show()
            self.manager_button.show()
            self.admin_button.show()

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    from login_window import LoginWindow
    
    db = Database()
    window = LoginWindow(db)
    window.show()
    
    sys.exit(app.exec())