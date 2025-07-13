import os
import logging
import psycopg
from dotenv import load_dotenv
import logging
import sys

load_dotenv()


log_dir = 'logs'
file_name = 'transform_schemas.log'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, file_name),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def connect_to_db():
    conn = psycopg.connect(
            host = os.getenv('DB_HOST'),
            password = os.getenv('DB_PASSWORD'),
            dbname = 'jobs_db',
            user = 'postgres',
            port = 5432,
            sslmode = "require",
            connect_timeout = 10
        )
    return conn

def create_schema_in_postgres(schema_name: str):
    conn = None
    cursor = None

    try:
        conn = connect_to_db()
        print('connection was succesful')
        cursor = conn.cursor()

        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema_name};')
        print(f'created schema {schema_name}')

        cursor.execute(f'GRANT ALL ON SCHEMA {schema_name} TO postgres;')
        print(f'granted all permission to schema {schema_name} to user postgres')

        conn.commit()

        return True

    except Exception as e:
        print(f'Something is not working. Error {e}')
        return False 
    
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

def change_schema_name(existing_schema: str, new_name_schema:str):
    conn = None
    cursor = None

    try:
        conn = connect_to_db()
        print('connection succesful')

        conn.execute(f'ALTER SCHEMA {existing_schema} RENAME TO {new_name_schema};')
        conn.commit()
        print(f'Schema {existing_schema} successfully renamed to {new_name_schema}')

    except Exception as e:
        print(f'Something went wrong. Error: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def set_default_schema(schema_name):
    conn = None
    cursor = None

    try:
        conn = connect_to_db()
        print('connection succesful')

        conn.execute(f'SET search_path TO Raw;')
        conn.commit()
        print(f'Set {schema_name} to default Schema')

    except Exception as e:
        print(f'Something went wrong. Error: {e}')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# create_schema_in_postgres('Prod')
# change_schema_name('Transform','Staging')
# set_default_schema('Raw')