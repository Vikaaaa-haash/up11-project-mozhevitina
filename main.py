import sys
import os
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'logic'))
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database 

logging.basicConfig(
    filename='app.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ювелирный — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.db = Database()
        
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

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


from discount import calculate_price  


def create_card(product):
    p_id = product[0]
    category = product[1]
    name = product[2]
    production = product[3]
    composition = product[4]
    price = product[5]
    image_name = product[6]

    # ДЗ
    if image_name is not None and str(image_name).strip() != "":
        image_path = f"resources/{image_name}"
    else:
        image_path = None

    if image_path and os.path.exists(image_path):
        pixmap = QPixmap(image_path)
    else:
        # Логирование отсутствующих файлов
        if image_name:
            logging.warning(f"Файл не найден: {image_name}. Использована заглушка.")
        else:
            logging.warning(f"У товара '{name}' (ID: {p_id}) не указано изображение. Использована заглушка.")
        pixmap = QPixmap("resources/picture.png")

    try:
        final_price = calculate_price(name, float(price))
        if final_price is None:
            final_price = float(price)
    except Exception as e:
        logging.error(f"Ошибка при расчете скидки: {e}")
        final_price = float(price)

    # --- 3. Подсветка (красным, если цена < 2000) ---
    bg_color = "#FF8080" if float(price) < 2000 else "#FFFFFF"

    # --- 4. Создание карточки ---
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
    
    # Изображение
    image_label = QLabel()
    image_label.setFixedSize(100, 100)
    image_label.setAlignment(Qt.AlignCenter)
    if not pixmap.isNull():
        image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        image_label.setText("[НЕТ ФОТО]")
    main_layout.addWidget(image_label)
    
    # Текст
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
    
    # Цена (со скидкой)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())