import psycopg2

def calculate_price(item_name, base_price):
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="practice_db",
            user="postgres", password="123"
        )
        cursor = conn.cursor()

        # 1. Дополнительный запрос: получаем название товара из БД
        # (Так как мы передаем название, запрос ищет по name)
        cursor.execute("SELECT name FROM products WHERE name = %s", (item_name,))
        name_row = cursor.fetchone()
        product_name = name_row[0] if name_row else item_name

        # 2. Основной запрос: считаем заказы за месяц
        cursor.execute("""
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.id 
            WHERE oi.product_name = %s 
              AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """, (item_name,))

        result = cursor.fetchone()
        orders_count = result[0]

        cursor.close()
        conn.close()

        if orders_count == 0:
            final_price = float(base_price) * 0.75
            discount_size = 25.0
        else:
            final_price = float(base_price)
            discount_size = 0.0

        print(f"Товар: {product_name} | Итог: {final_price} | Скидка: {discount_size}%")
        return (final_price, discount_size)

    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None

# Тестовый запуск
if __name__ == "__main__":
    result = calculate_price('Кольцо Линия', 2990)
    print(f"Результат (кортеж): {result}")