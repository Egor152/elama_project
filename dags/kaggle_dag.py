from airflow import DAG
from datetime import datetime
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

import zipfile
import csv
import logging 
log = logging.getLogger(__name__)
pg_hook = PostgresHook(postgres_conn_id='pg_connect')


args = {
   'owner': 'airflow',  # Информация о владельце DAG
   'start_date': datetime(2024, 12, 31),  # Время начала выполнения пайплайна
}

curl_command = """
curl -L -o /opt/airflow/data/advertisement-click-on-ad.zip\
  https://www.kaggle.com/api/v1/datasets/download/gabrielsantello/advertisement-click-on-ad
"""

def unpack_zipfile(filename, path_to_zip, path_to_extract):#/opt/airflow/dags/
    zip_file_path = path_to_zip
    file_to_extract = filename

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extract(file_to_extract, path_to_extract)


def insert_data():
    pg_conn = pg_hook.get_conn()
    connection = pg_conn
    cur = connection.cursor()
    with open('/opt/airflow/data/advertising.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Пропускаем хэдэр с названиями столбцов
        for row in reader:
            cur.execute("""
                        INSERT INTO stg.adv(daily_time_spent_on_site, age, area_income, daily_internet_usage, ad_topic_line, city, male, country, "timestamp", clicked_on_ad)
                        VALUES (%s, %s, %s,
                                %s, %s, %s,
                                %s, %s, %s, %s)
                            """, row)
        connection.commit()
        log.info(f'Данные вставились в БД')


with DAG(
    dag_id='kaggle_dag',  # Имя DAG
    schedule_interval=None,  # Периодичность запуска, например, "00 15 * * *"
    default_args=args,  # Базовые аргументы
) as dag:

    start_task = BashOperator(
    task_id='start_task',
    bash_command='echo "Here we start! "', 
    dag=dag,
    )

    creating_schema_task = PostgresOperator(
        task_id = 'creating_schema_stg',
        postgres_conn_id = 'pg_connect',
        sql = 'sql/creating_schema.sql',
        dag=dag,
    )

    clearing_table_task = PostgresOperator(
        task_id = 'clearing_table_task',
        postgres_conn_id = 'pg_connect',
        sql = 'sql/clearing_table.sql',
        dag=dag,
    )

    get_data_from_kaggle = BashOperator(
        task_id='get_data_from_kaggle',
        bash_command=curl_command,
        dag=dag,)

    unpack_data = PythonOperator(
        task_id = 'unpack_kaggle_data',
        python_callable=unpack_zipfile,
        op_kwargs={'filename':'advertising.csv',
                    'path_to_zip':'/opt/airflow/data/advertisement-click-on-ad.zip',
                    'path_to_extract':'/opt/airflow/data'}
        )
    
    load_data = PythonOperator(
        task_id = 'load_data',
        python_callable=insert_data
        )

    end_task = BashOperator(
    task_id='end_task',
    bash_command='echo "Here we end! "',
    dag=dag,
    )

start_task  >> creating_schema_task >> clearing_table_task >> get_data_from_kaggle >> unpack_data >> load_data >> end_task
                        
