import pandas as pd
import psycopg2
from database import Database # Используем ваш класс Database для подключения

def import_data_from_excel(file_path):
    print("Чтение Excel-файла...")
    # Читаем Excel (предполагаем, что файл называется Users_import.xlsx)
    df = pd.read_excel(file_path)
    
    db = Database()
    conn = db.get_connection()
    if not conn:
        print("Ошибка подключения к БД")
        return
        
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    print("Обновление данных в БД...")
    for index, row in df.iterrows():
        # Берем данные из колонок Excel
        last_name = str(row['Фамилия']).strip() if pd.notna(row['Фамилия']) else ''
        first_name = str(row['Имя']).strip() if pd.notna(row['Имя']) else ''
        middle_name = str(row['Отчество']).strip() if pd.notna(row['Отчество']) else ''
        
        login = str(row['Логин']).strip()
        role = str(row['Роль']).strip()
        
        # Обновляем существующего пользователя
        try:
            cursor.execute("""
                UPDATE users 
                SET last_name = %s, first_name = %s, middle_name = %s 
                WHERE login = %s
            """, (last_name, first_name, middle_name, login))
            success_count += 1
        except Exception as e:
            print(f"Ошибка при обновлении {login}: {e}")
            conn.rollback()
            error_count += 1
            
    conn.commit()
    cursor.close()
    db.release_connection(conn)
    print(f"Готово! Обновлено пользователей: {success_count}. Ошибок: {error_count}.")

if __name__ == "__main__":
    # Укажите точное имя вашего Excel-файла
    excel_file = "Users_import.xlsx" 
    import_data_from_excel(excel_file)