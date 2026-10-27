import openpyxl
import os
from app.database import Database

def import_users():
    possible_paths = [
        "Users_import.xlsx",
        os.path.join(os.path.expanduser("~"), "Desktop", "Users_import.xlsx")
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
            
    if not file_path:
        print("ОШИБКА: Файл Users_import.xlsx не найден!")
        return

    print(f"Найден файл: {file_path}")
    
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    
    db = Database()
    conn = db.get_connection()
    if not conn:
        print("Ошибка подключения к БД")
        return
        
    cursor = conn.cursor()
    added_count = 0
    updated_count = 0
    
    print("Проверка и добавление пользователей в БД...")
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[3]: 
            continue
            
        last_name = str(row[0]).strip() if row[0] else ''
        first_name = str(row[1]).strip() if row[1] else ''
        middle_name = str(row[2]).strip() if row[2] else ''
        login = str(row[3]).strip()
        role = str(row[4]).strip()

        if role == "Авторизованный пользователь":
            role = "Клиент"
        
        cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
        exists = cursor.fetchone()
        
        try:
            if exists:
                cursor.execute("""
                    UPDATE users 
                    SET last_name = %s, first_name = %s, middle_name = %s, role = %s
                    WHERE login = %s
                """, (last_name, first_name, middle_name, role, login))
                updated_count += 1
            else:
                cursor.execute("""
                    INSERT INTO users (login, role, last_name, first_name, middle_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (login, role, last_name, first_name, middle_name))
                added_count += 1
            conn.commit() 
        except Exception as e:
            print(f"Ошибка с пользователем {login}: {e}")
            conn.rollback() 
            
    conn.commit()
    cursor.close()
    db.release_connection(conn)
    print(f"ГОТОВО! Добавлено новых: {added_count}. Обновлено старых: {updated_count}.")

if __name__ == "__main__":
    import_users()