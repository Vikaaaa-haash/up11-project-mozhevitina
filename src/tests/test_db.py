from app.database import Database

db = Database()
conn = db.get_connection()

if conn is None:
    print("Не удалось подключиться к базе данных.")
else:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()
    print(f"Количество товаров: {result[0]}")
    cursor.close()
    db.release_connection(conn)

db.close_all()