import os

# 1. Проверяем файл-заглушку
picture_path = "resources/picture.png"
if os.path.exists(picture_path):
    print(f"Файл {picture_path} — СУЩЕСТВУЕТ")
else:
    print(f"Файл {picture_path} — НЕ СУЩЕСТВУЕТ")

# 2. Проверяем файл товара (из твоей базы)
image_path = "resources/IMG_11_001.png"
if os.path.exists(image_path):
    print(f"Файл {image_path} — СУЩЕСТВУЕТ")
else:
    print(f"Файл {image_path} — НЕ СУЩЕСТВУЕТ (сработает заглушка)")