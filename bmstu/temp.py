import psycopg2

with open('/Users/user/Downloads/imgonline-com-ua-Resize-mRTj8ocOG9V8.jpg', 'rb') as file:
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
    WHERE type = 'Карта';
"""

# Обновление значения столбца icon
cursor.execute(update_query, (image_binary,))

# Сохранение изменений и закрытие соединения
connection.commit()
cursor.close()
connection.close()
