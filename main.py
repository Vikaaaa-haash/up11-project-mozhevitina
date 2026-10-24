import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Ювелирный — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        # Создание центрального виджета
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Добавление логотипа
        logo = QLabel()
        pixmap = QPixmap("resources/logo.png")
        logo.setPixmap(pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        layout.addStretch() 
        layout.addWidget(logo)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: 'Calibri';
            }
            QLabel {
                color: #000000;
            }
        """)

        layout.addWidget(logo)

        title = QLabel("Ювелирный магазин")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #70B2AF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        version = QLabel("v1.0")
        version.setStyleSheet("font-size: 14px; color: #888888;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)


        layout.addStretch() 

    def closeEvent(self, event):
        # Закрываем все соединения в пуле
        if self.db:
            self.db.close_all()
        # Подтверждаем закрытие окна
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())