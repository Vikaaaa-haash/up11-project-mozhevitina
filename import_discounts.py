import csv
from database import Database

def import_discounts():
    # Читаем файл с заказами, чтобы взять оттуда проценты
    file_path = "Orders_analytics.csv"
    
    db = Database()
    conn = db.get_connection()
    if not conn:
        print("Ошибка подключения к БД")
        return
        
    cursor = conn.cursor()
    
    # 1. Собираем уникальные скидки из файла заказов
    discounts = set()
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader) # Пропускаем заголовок
            for row in reader:
                if len(row) >= 6:
                    try:
                        discount = int(row[5]) # Колонка discount_percent
                        discounts.add(discount)
                    except ValueError:
                        pass
    except FileNotFoundError:
        print("Файл Orders_analytics.csv не найден! Убедитесь, что он в папке с проектом.")
        return

    print(f"Найденные уникальные скидки в файле: {sorted(discounts)}")
    
    # 2. Назначаем эти скидки товарам по кругу (чтобы у всех были разные)
    cursor.execute("SELECT id FROM products")
    product_ids = [row[0] for row in cursor.fetchall()]
    
    discount_list = sorted(list(discounts))
    if not discount_list:
        print("Не найдено скидок для импорта.")
        return
        
    updated_count = 0
    for i, p_id in enumerate(product_ids):
        # Берем скидку из списка по очереди (циклически)
        discount = discount_list[i % len(discount_list)]
        
        cursor.execute("UPDATE products SET discount_percent = %s WHERE id = %s", (discount, p_id))
        updated_count += 1
        
    conn.commit()
    cursor.close()
    db.release_connection(conn)
    print(f"ГОТОВО! Обновлено товаров: {updated_count}. Каждому товару назначена скидка из файла!")

if __name__ == "__main__":
    import_discounts()