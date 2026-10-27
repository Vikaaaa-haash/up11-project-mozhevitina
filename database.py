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

    def get_products(self, search="", category="Все категории", production="Все производители", sort_order="По возрастанию"):
        """
        Получает список товаров из БД с учетом поиска, фильтров и сортировки.
        Возвращает список кортежей с данными товаров.
        """
        conn = self.get_connection()
        if not conn: return []
        cursor = conn.cursor()

        query = """
            SELECT id, category, subcategory, image, name, production, description, composition, price, stock, discount_percent 
            FROM products 
            WHERE (name ILIKE %s OR description ILIKE %s)
        """
        params = [f"%{search}%", f"%{search}%"]
        
        # Фильтр по категории
        if category != "Все категории":
            query += " AND category = %s"
            params.append(category)

        if production != "Все производители":
            query += " AND production = %s"
            params.append(production)
            
        # Сортировка
        if sort_order == "По возрастанию":
            query += " ORDER BY price ASC"
        elif sort_order == "По убыванию":
            query += " ORDER BY price DESC"
        elif sort_order == "По названию (А-Я)": 
            query += " ORDER BY name ASC"
            
        try:
            cursor.execute(query, tuple(params))
            products = cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении товаров: {e}")
            products = []
            
        cursor.close()
        self.release_connection(conn)
        return products

    def get_categories(self):
        """Получает список уникальных категорий из БД"""
        conn = self.get_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT category FROM products")
            categories = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Ошибка при получении категорий: {e}")
            categories = []
        finally:
            cursor.close()
            self.release_connection(conn) 
            
        return categories
    
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
            conn.commit()  
            cursor.close()
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при изменении данных: {e}")
            conn.rollback()  
            return False
        finally:
            self.release_connection(conn)
    def get_productions(self):
        conn = self.get_connection()
        if not conn: return []
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT production FROM products")
        res = [row[0] for row in cursor.fetchall()]
        cursor.close()
        self.release_connection(conn)
        return res