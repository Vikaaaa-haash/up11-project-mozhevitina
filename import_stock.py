import csv
from app.database import Database

def import_stock():
    file_path = "Stock_Items_import.csv"
    
    db = Database()
    conn = db.get_connection()
    if not conn:
        print("Ошибка подключения к БД")
        return
        
    cursor = conn.cursor()
    
    cursor.execute("UPDATE products SET stock = 0")
    conn.commit()
    
    print(f"Чтение файла {file_path}...")
    stock_dict = {}
    
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            first_line = file.readline()
            delimiter = ';' if ';' in first_line else ','
            file.seek(0)
            
            reader = csv.reader(file, delimiter=delimiter)
            next(reader) 
            
            for row in reader:
                if not row or len(row) < 4:
                    continue
                
                name = row[0].strip()
                try:
                    qty_str = row[3].strip().replace(',', '.') 
                    qty = int(float(qty_str)) 
                except ValueError:
                    qty = 0
                    
                if name in stock_dict:
                    stock_dict[name] += qty
                else:
                    stock_dict[name] = qty
                    
        print(f"Найдено уникальных товаров в файле: {len(stock_dict)}")
        print("Обновление остатков в БД (поиск по частичному совпадению)...")
        
        updated_count = 0
        for name, total_qty in stock_dict.items():
            cursor.execute("UPDATE products SET stock = %s WHERE name LIKE %s", (total_qty, f"%{name}%"))
            if cursor.rowcount > 0:
                updated_count += cursor.rowcount
            
        conn.commit()
        print(f"ГОТОВО! Обновлено записей в таблице: {updated_count}.")
        
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)

if __name__ == "__main__":
    import_stock()