import psycopg2
import csv
from psycopg2 import sql
import json

with open("db_config.json", 'r') as file:
    db_config =  json.load(file)
    # Подключаемся к базе данных
connection = psycopg2.connect(
    dbname=db_config["dbname"],
    user=db_config["user"],
    password=db_config["password"],
    host=db_config["host"],
    port=db_config["port"]
)
cur = connection.cursor()

create_table_query = '''
DROP TABLE mutations;
CREATE TABLE IF NOT EXISTS mutations (
    id SERIAL PRIMARY KEY,
    AssociatedDiseases VARCHAR(200),
    Allele VARCHAR(100),
    Position NUMERIC,
    RNA VARCHAR(100),
    count NUMERIC DEFAULT 1
);
'''

# Выполнение запроса на создание таблицы
cur.execute(create_table_query)

# Сохранение изменений
connection.commit()

# Открываем CSV файл
with open('ConfirmedMutations_MITOMAP_Foswiki.csv', 'r') as f:
    # Пропускаем строку с заголовками
    next(f)
    # Загружаем данные в таблицу
    cur.copy_from(f, 'mutations', sep=',', columns=('associateddiseases', 'allele', 'position','rna'))

# Сохраняем изменения и закрываем соединение
connection.commit()
cur.close()
connection.close()
