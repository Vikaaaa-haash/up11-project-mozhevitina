import logging
import psycopg2

# Настройка логирования
logging.basicConfig(
    filename='app.log',          # Файл, куда будут записываться ошибки
    level=logging.ERROR,         # Уровень (только ошибки)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_price_jewelry(item_name, base_price):
    if not isinstance(item_name, str) or not item_name:
        print("Ошибка: название должно быть непустой строкой")
        return None
    if not isinstance(base_price, (int, float)):
        print("Ошибка: цена должна быть числом")
        return None
    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="practice_db",
            user="postgres", password="123"
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.id 
            WHERE oi.product_name = %s 
              AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """, (item_name,))

        result = cursor.fetchone()

        if result is None:
            print("Ошибка: нет результата")
            return None

        orders_count = result[0]

        if orders_count == 0:
            return base_price * 0.75
        else:
            return base_price

    except psycopg2.Error as e:
        logging.error(f"Ошибка БД: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("--- Тест 1: Неверный тип названия ---")
    calculate_price_jewelry(123, 1000)
    
    print("\n--- Тест 2: Отрицательная цена ---")
    calculate_price_jewelry('Кольцо Линия', -100)
    
    print("\n--- Тест 3: Несуществующий товар ---")
    print(f"Результат: {calculate_price_jewelry('Несуществующий товар', 1000)}")

def update_price(product_id, new_price):
    if not isinstance(product_id, int):
        print("Ошибка: ID должен быть числом")
        return False
    if not isinstance(new_price, (int, float)) or new_price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return False

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="practice_db",
            user="postgres", password="123"
        )
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE products SET price = %s WHERE id = %s",
            (new_price, product_id)
        )
        
        if cursor.rowcount == 0:
            print("Ошибка: товар с таким ID не найден")
            return False

        conn.commit()
        print("Цена обновлена")
        return True

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


if __name__ == "__main__":
    update_price(1, 3500)       
    update_price(99999, 3500)   
    update_price(1, -100)       