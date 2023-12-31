import psycopg2

with open('/Users/user/Downloads/personal-2.png', 'rb') as file:
    image_binary = file.read()


# Подключение к базе данных PostgreSQL
connection = psycopg2.connect(
    database="Bankings",
    user="postgres",
    password="5441",
    host="localhost",
    port="5433"
)

# Создание курсора
cursor = connection.cursor()

# SQL-запрос для вставки данных
update_query = """
    UPDATE account
    SET icon = %s
    WHERE type = 'Кредитный счет';
"""

# Обновление значения столбца icon
cursor.execute(update_query, (image_binary,))

# Сохранение изменений и закрытие соединения
connection.commit()
cursor.close()
connection.close()
