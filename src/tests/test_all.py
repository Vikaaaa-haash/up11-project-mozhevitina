import psycopg2
from discount import calculate_price

conn = psycopg2.connect(
    host="localhost", port=5432, database="practice_db",
    user="postgres", password="123"
)
cursor = conn.cursor()

cursor.execute("SELECT id, name, price FROM products")
products = cursor.fetchall()

for p in products:
    product_id, name, price = p[0], p[1], float(p[2])
    final_price = calculate_price(name, price)
    
    print(f"{product_id} | {name} | Базовая: {price} | Итоговая: {final_price}")

cursor.close()
conn.close()