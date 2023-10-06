import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

def get_account_by_name(connection, account_name):
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM account WHERE name = %s", (account_name,))
        account = cursor.fetchone()
        cursor.close()
        return account

    except Error as e:
        print("Ошибка при работе с PostgreSQL", e)
        return None

def change_avaialability(connection, account_name):
    cursor = connection.cursor()

    sql_query = """
    UPDATE account_status
    SET frozen = NOT frozen
    WHERE id = (SELECT account_status_refer FROM account WHERE name = %s);
    """

    cursor.execute(sql_query, (account_name,))

    connection.commit()
    cursor.close()