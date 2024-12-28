import psycopg2
import os
import json
def parse_fasta(file_path):
    """Чтение последовательности из файла FASTA без использования SeqIO."""
    sequence = []
    with open(file_path, 'r') as file:
        for line in file:
            if not line.startswith('>'):
                sequence.append(line.strip())
    return ''.join(sequence)
    
def extract_context(array1, array2, index1, index2):
    """
    Выводит 10 предыдущих и 10 следующих символов из массивов по заданным индексам.
    
    :param array1: Первый массив символов (список или строка)
    :param array2: Второй массив символов (список или строка)
    :param index1: Индекс текущей позиции в первом массиве
    :param index2: Индекс текущей позиции во втором массиве
    """
    # Конвертируем входные данные в строки, если они списки
    array1 = ''.join(array1) if isinstance(array1, list) else array1
    array2 = ''.join(array2) if isinstance(array2, list) else array2

    def context(array, index):
        """Функция для получения контекста символа."""
        start = max(0, index - 10)
        end = min(len(array), index + 11)
        return array[start:index], array[index + 1:end]

    # Контекст для массива 1
    prev1, next1 = context(array1, index1)
    current1 = array1[index1] if 0 <= index1 < len(array1) else None

    print(f"{prev1}{current1}{next1}  {index1}")

    # Контекст для массива 2
    prev2, next2 = context(array2, index2)
    current2 = array2[index2] if 0 <= index2 < len(array2) else None

    print(f"{prev2}{current2}{next2}  {index2}")
    print("          _          ")


def find_mutations(reference, query):
    """Поиск мутаций между референсом и данным геномом с учётом вставок, удалений и инверсий."""
    mutations = []
    ref_len = len(reference)
    query_len = len(query)
    i, j = 0, 0

    while i < ref_len and j < query_len:
        if reference[i] == query[j]:
            i += 1
            j += 1
        else:
            extract_context(reference, query, i, j)
            if i > ref_len - 4 or j > query_len - 4 or reference[i+1] == query[j+1] and reference[i+2] == query[j+2] and reference[i+3] == query[j+3]:
                mutations.append(f"m.{i + 1}{reference[i]}>{query[j]}")
                print(f"m.{i + 1}{reference[i]}>{query[j]}")
                i += 1
                j += 1
            elif reference[i+1] == query[j] and reference[i+2] == query[j+1] and reference[i+3] == query[j+2]:
                mutations.append(f"m.{i + 1}del{reference[i]}")
                print(f"m.{i + 1}del{reference[i]}")
                extract_context(reference, query, i, j)
                i += 2
                j += 1
            else:
            # Найти начало и конец расхождения
                ref_start, query_start = i, j
                while i < ref_start + 10 and j < query_len - 2 and i < ref_len - 2 and (reference[i] != query[j] or reference[i+1] != query[j+1] or reference[i+2] != query[j+2]):
                    i += 1
                if i == ref_start + 10:
                    i = ref_start
                    while j < query_start + 10 and j < query_len - 2 and i < ref_len - 2 and (reference[i] != query[j] or reference[i+1] != query[j+1] or reference[i+2] != query[j+2]):
                        j += 1
                    if j != query_start + 10:
                        mutations.append(f"m.{ref_start + 1}ins{query[query_start:j]}")
                        print(f"m.{ref_start + 1}ins{query[query_start:j]}")
                    else:
                        j = query_start
                else:
                    mutations.append(f"m.{ref_start + 1}del{reference[ref_start:i]}")
                    print(f"m.{ref_start + 1}del{reference[ref_start:i]}")
                while i < ref_len and j < query_len and reference[i] != query[j]:
                    i += 1
                    j += 1
                ref_end, query_end = i, j

                

    # Проверить оставшиеся элементы в референсе или query
    if i < ref_len:
        mutations.append(f"DEL:{i + 1}-{ref_len}")
    if j < query_len:
        mutations.append(f"INS:{j + 1}-{query_len}")

    return mutations

def check_and_add_mutation_to_db(connection, mutation, name):
    """Проверка наличия мутации в БД и добавление её, если она отсутствует."""
    with connection.cursor() as cursor:
        # Проверяем наличие мутации в столбце allele
        cursor.execute("SELECT * FROM mutations WHERE allele = %s", (mutation,))
        result = cursor.fetchone()

        if not result:
            # Если мутации нет, добавляем её в таблицу
            cursor.execute("INSERT INTO mutations (allele) VALUES (%s)", (mutation,))
            #print(f"Мутация {mutation} добавлена в базу данных.")
        else:
            cursor.execute("UPDATE mutations SET count = count+1 WHERE allele = %s", (mutation,))
            cursor.execute("INSERT INTO samples (name, mutation) VALUES (%s, %s)", (name, result[0]))

def main():
    # Настройки подключения к базе данных
    db_config = {
        "dbname": "your_database_name",
        "user": "your_user",
        "password": "your_password",
        "host": "localhost",
        "port": "5432",
    }

    # Пути к файлам
    reference_fasta = "/home/katerina/Mitohondrion/Healthy/NC_012920.1.fasta"
    folder_path = "/home/katerina/Mitohondrion/Mutated/"
    extension = ".fasta"
    #query_fasta = "/home/katerina/Mitohondrion/Mutated/OR438442.1.fasta"
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

    
    with connection.cursor() as cursor:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS samples (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            mutation NUMERIC
        );
        '''
    
        # Выполнение запроса на создание таблицы
        cursor.execute(create_table_query)

    # Сохранение изменений
    connection.commit()

    # Читаем референсную последовательность
    reference_sequence = parse_fasta(reference_fasta)
    #query_sequence = parse_fasta(query_fasta)
    
    for file_name in os.listdir(folder_path):
        if file_name.endswith(extension):
            file_path = os.path.join(folder_path, file_name)
            query_sequence = parse_fasta(file_path)

            # Находим мутации
            mutations = find_mutations(reference_sequence, query_sequence)

            for mutation in mutations:
                check_and_add_mutation_to_db(connection, mutation, file_name)
            # Сохраняем изменения
            connection.commit()
        
        # Закрываем соединение с базой данных
    connection.close()

if __name__ == "__main__":
    main()

