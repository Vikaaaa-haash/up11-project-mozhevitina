import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'logic')) 
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QPushButton, QMessageBox
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database
from discount import calculate_price

logging.basicConfig(
    filename='app.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_card(product):
    p_id = product[0]
    category = product[1]
    name = product[2]
    production = product[3]
    composition = product[4]
    price = product[5]
    image_name = product[6]

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

    # Скидка
    try:
        final_price = calculate_price(name, float(price))
        if final_price is None:
            final_price = float(price)
    except Exception as e:
        logging.error(f"Ошибка при расчете скидки: {e}")
        final_price = float(price)

    # Подсветка
    bg_color = "#FF8080" if float(price) < 2000 else "#FFFFFF"

    card = QWidget()
    card.setStyleSheet(f"""
        QWidget {{
            background-color: {bg_color};
            border: 1px solid #70B2AF;
            border-radius: 5px;
            margin-bottom: 5px;
        }}
    """)
    
    main_layout = QHBoxLayout()
    
    image_label = QLabel()
    image_label.setFixedSize(100, 100)
    image_label.setAlignment(Qt.AlignCenter)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        image_label.setText("[НЕТ ФОТО]")
    main_layout.addWidget(image_label)
    
    text_layout = QVBoxLayout()
    
    title = QLabel(f"{production} | {name}")
    title.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; border: none;")
    text_layout.addWidget(title)
    
    cat_label = QLabel(f"Категория: {category}")
    cat_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(cat_label)
    
    comp_label = QLabel(f"Состав: {composition}")
    comp_label.setStyleSheet("color: #555555; border: none;")
    text_layout.addWidget(comp_label)
    
    main_layout.addLayout(text_layout)
    
    if final_price < float(price):
        price_text = f"<s>{int(price)} ₽</s><br><b style='color:#70B2AF;'>{int(final_price)} ₽</b>"
    else:
        price_text = f"<b style='color:#70B2AF;'>{int(price)} ₽</b>"

    price_label = QLabel(price_text)
    price_label.setStyleSheet("font-size: 18px; border: none;")
    price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    main_layout.addWidget(price_label)
    
    card.setLayout(main_layout)
    return card


class MainWindow(QMainWindow):
    # ДОБАВИЛИ user_fio в параметры конструктора
    def __init__(self, user_role=None, user_fio=None):
        super().__init__()
        self.user_role = user_role
        self.user_fio = user_fio 
        self.db = Database()
        
        self.setWindowTitle("Ювелирный — Каталог")
        self.resize(900, 700)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        print(f"DEBUG: В главное окно передана роль: {self.user_role}, ФИО: {self.user_fio}")
        
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        
        top_layout = QHBoxLayout()
        
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(logo)
        
        title = QLabel("Ювелирный магазин")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF;")
        top_layout.addWidget(title)
        top_layout.addStretch()

        # ДОБАВЛЯЕМ ОТОБРАЖЕНИЕ ФИО ПОЛЬЗОВАТЕЛЯ
        if self.user_fio:
            self.fio_label = QLabel(self.user_fio)
            self.fio_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; margin-right: 15px;")
            top_layout.addWidget(self.fio_label)

        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        top_layout.addWidget(self.order_button)
        top_layout.addWidget(self.manager_button)
        top_layout.addWidget(self.admin_button)

        # ДОБАВЛЯЕМ КНОПКУ ВЫХОД
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #FF8080; color: white; font-weight: bold; padding: 5px 15px;")
        self.logout_button.clicked.connect(self.logout)
        top_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(top_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        catalog_container = QWidget()
        catalog_layout = QVBoxLayout()
        catalog_container.setLayout(catalog_layout)
        
        products = self.db.get_products()
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
        # По умолчанию (Гость) — скрываем все кнопки
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        
        # Показываем кнопки по роли
        if self.user_role == "Клиент":
            self.order_button.show()
        elif self.user_role == "Менеджер":
            self.order_button.show()
            self.manager_button.show()
        elif self.user_role == "Администратор":
            self.order_button.show()
            self.manager_button.show()
            self.admin_button.show()

    def logout(self):
        reply = QMessageBox.question(
            self, 'Выход', 
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Возвращаемся к окну входа
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