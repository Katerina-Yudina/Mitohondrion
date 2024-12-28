import subprocess
import psycopg2
import os
import json

def run_quast_and_store_results(assembly_file, reference_file, db_config):
    """
    Запускает QUAST и сохраняет результаты в базу данных.

    :param assembly_file: путь к файлу сборки
    :param reference_file: путь к референсному файлу
    :param db_config: словарь с параметрами подключения к БД
    """
    try:
        # Папка для хранения результата
        output_dir = "quast_output"
        os.makedirs(output_dir, exist_ok=True)

        # Запуск QUAST
        subprocess.run(
            ["quast.py", "-r", reference_file, "-o", output_dir, assembly_file, "--space-efficient"],
            check=True
        )

        # Чтение ключевых метрик из файла report.txt
        report_path = os.path.join(output_dir, "report.txt")
        if not os.path.exists(report_path):
            raise FileNotFoundError(f"Файл отчета {report_path} не найден!")

        with open(report_path, "r") as report:
            data = {}
            for line in report:
                if "Total length (>= 0 bp)  " in line:
                    data["total_length"] = int(line.split()[5])
                elif "N50  " in line:
                    data["n50"] = int(line.split()[1])
                elif "GC (%)                       " in line:
                    data["gc_content"] = float(line.split()[2])
                elif "# contigs  " in line:
                    data["num_contigs"] = int(line.split()[2])
                    
        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"]
        )
        cursor = conn.cursor()

        # Вставка данных в таблицу
        insert_query = """
            CREATE TABLE IF NOT EXISTS quast_results (
                id SERIAL PRIMARY KEY,
                assembly_file VARCHAR(100),
                total_length NUMERIC,
                n50 NUMERIC,
                gc_content NUMERIC,
                num_contigs NUMERIC
            );
            INSERT INTO quast_results (assembly_file, total_length, n50, gc_content, num_contigs)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            os.path.basename(assembly_file),
            data["total_length"],
            data["n50"],
            data["gc_content"],
            data["num_contigs"]
        ))

        # Завершение транзакции
        conn.commit()

        print(f"Результаты QUAST успешно сохранены в БД: {data}")

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске QUAST: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

# Пример использования
if __name__ == "__main__":
    reference_file = "/home/katerina/Mitohondrion/Healthy/NC_012920.1.fasta"
    folder_path = "/home/katerina/Mitohondrion/Mutated/"
    extension = ".fasta"
    with open("db_config.json", 'r') as file:
        db_config =  json.load(file)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(extension):
            assembly_file = os.path.join(folder_path, file_name)
            run_quast_and_store_results(assembly_file, reference_file, db_config)
            
            
