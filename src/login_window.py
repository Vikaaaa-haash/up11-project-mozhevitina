from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        
        self.setWindowTitle("Авторизация — Ювелирный")
        self.resize(350, 200)
        
        layout = QVBoxLayout()
        
        # Логин
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)
        
        # Горизонтальный слой для кнопок
        btn_layout = QHBoxLayout()
        
        # Кнопка "Войти"
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        btn_layout.addWidget(self.login_button)
        
        # Кнопка "Отмена" (ДЗ)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close) # Закрывает окно
        btn_layout.addWidget(self.cancel_button)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()
        
        # 1. (ДЗ)
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        # 2. Подключение к БД
        conn = self.db.get_connection()
        if conn is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        # 3. Проверка логина в БД
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT login, role FROM users WHERE login = %s", (login,))
            result = cursor.fetchone()
            cursor.close()
            self.db.release_connection(conn)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка запроса: {e}")
            return

        # 4. Анализ результата
        if result is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин")
        else:
            self.user_login = result[0]
            self.user_role = result[1]
            
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {self.user_role}!")
            
            # 5. Переход к главному окну
            from main import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()