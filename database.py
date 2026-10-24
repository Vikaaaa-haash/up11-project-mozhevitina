import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host="localhost", port=5432, database="practice_db",
                user="postgres", password="123"
            )
        except psycopg2.Error as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None

    def release_connection(self, conn):
        self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()

    def get_products(self):
        """Возвращает список всех товаров с остатками (для ювелирки)"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, category, name, production, 
                    composition, price, image, 0 as total_quantity
                FROM products
                ORDER BY id
            """)
            products = cursor.fetchall()
            cursor.close()
            return products
        except psycopg2.Error as e:
            print(f"Ошибка при запросе: {e}")
            return []
        finally:
            self.release_connection(conn)
    def execute_query(self, sql, params=None):
        """Универсальный метод для SELECT-запросов"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        """Универсальный метод для INSERT/UPDATE/DELETE"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()  # Важно для сохранения изменений!
            cursor.close()
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при изменении данных: {e}")
            conn.rollback()  # Откатываем изменения при ошибке
            return False
        finally:
            self.release_connection(conn)