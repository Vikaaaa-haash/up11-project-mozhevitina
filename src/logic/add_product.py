import psycopg2

def add_product(name, price, category):
    if not name or not isinstance(name, str):
        print("Ошибка: имя не может быть пустым и должно быть строкой")
        return False
    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return False
    if not isinstance(category, str) or not category:
        print("Ошибка: категория должна быть непустой строкой")
        return False

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="practice_db",
            user="postgres", password="123"
        )
        cursor = conn.cursor()

        # 3. INSERT (вставляем в колонки category, name, price)
        cursor.execute("""
            INSERT INTO products (category, name, price)
            VALUES (%s, %s, %s)
        """, (category, name, price))

        try:
            conn.commit()
            print(f"Товар '{name}' успешно добавлен")
            return True
        except psycopg2.Error as e:
            print(f"Ошибка при сохранении: {e}")
            return False

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Тест 1: Пустое имя ---")
    add_product("", 1000, "Кольца")
    
    print("\n--- Тест 2: Цена < 0 ---")
    add_product("Часы", -100, "Часы")
    
    print("\n--- Тест 3: Пустая категория (аналог 99999) ---")
    add_product("Часы", 1000, "")
    
    print("\n--- Тест 4: Всё правильно ---")
    add_product("Тестовые часы", 1000, "Часы")