#(Задание 2.3)
def check_login(login):
    if login == "admin":
        return "Вход разрешён"
    else:
        return "Ошибка: неверный логин"


#(Задание 3.2)
def calculate_price(price, has_orders):
    if not has_orders:
        return price * 0.75
    else:
        return price


#(Задание 4.2)
def check_order(size, quantity, stock):
    if size is None:
        return "Ошибка: выберите размер"
    if quantity <= 0:
        return "Ошибка: количество должно быть > 0"
    if quantity > stock:
        return "Ошибка: недостаточно на складе"
    return "Можно добавить в заказ"

if __name__ == "__main__":
    print("--- 1. Проверка входа ---")
    print(check_login("admin"))
    print(check_login("guest"))
    
    print("\n--- 2. Проверка скидки ---")
    print("Без заказов (1000 руб):", calculate_price(1000, False))
    print("С заказами (1000 руб):", calculate_price(1000, True))
    
    print("\n--- 3. Проверка заказа ---")
    print(check_order("M", 5, 10))
    print(check_order(None, 5, 10))
    