import subprocess
import os
import psycopg2

def run_script(script_path, args=""):
    try:
        subprocess.run(f"{script_path} {args}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_path}: {e}")
        exit(1)

def main():
    # 1. Проверка и запуск PostgreSQL (если требуется)
    print("Ensuring PostgreSQL is running...")
    run_script("sudo systemctl start postgresql")

    
    # 2. Проверить заполненность mitibase.txt
    mitibase_path = "Mutated/mitibase.txt"
    if not os.path.exists(mitibase_path) or os.stat(mitibase_path).st_size == 0:
        print(f"Файл {mitibase_path} пуст. Заполните его перед продолжением.")
        exit(1)

    # 3. Скачать образцы
    print("Downloading samples...")
    run_script("Mutated/necto.sh")

    # 4. Загрузка данных в базу
    print("Loading data into the database...")
    run_script("python3 downloadcsv.py")

    # 5. Запуск QUAST
    print("Running QUAST analysis...")
    run_script("python3 quast_launch.py")

    # 6. Поиск мутаций
    print("Finding mutations...")
    run_script("python3 findingmutations.py")

    # 7. Запуск дашборда Evidence
    print("Starting Evidence dashboard...")
    os.chdir("evidence")
    run_script("npm run sources")
    run_script("npm run dev")

if __name__ == "__main__":
    main()

