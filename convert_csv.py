# Скрипт для пересохранения CSV в чистый UTF-8
input_file = r'C:\Temp\Products_import.csv'
output_file = r'C:\Temp\products_utf8.csv'

# Пробуем прочитать в разных кодировках, пока не получится
for enc in ['windows-1251', 'cp1251', 'utf-8']:
    try:
        with open(input_file, 'r', encoding=enc) as f:
            content = f.read()
        print(f"Успешно прочитано в кодировке: {enc}")
        break
    except UnicodeDecodeError:
        continue

# Сохраняем в чистом UTF-8
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

print(f"Файл сохранён как: {output_file}")