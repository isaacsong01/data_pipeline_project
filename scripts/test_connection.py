import psycopg
import os
from dotenv import load_dotenv

load_dotenv(override=True)


def connect_to_db():
    print("DB_HOST=", os.getenv("DB_HOST"))
    print("DB_PASSWORD", os.getenv("DB_PASSWORD"))

    try:
        conn = psycopg.connect(
            host = os.getenv('DB_HOST'),
            dbname = "jobs_db",
            user = "postgres",
            password = os.getenv('DB_PASSWORD'),
            port = 5432,
            sslmode = "require",
            connect_timeout = 10
        )
        print("Connection Successful")
        return conn

    except Exception as e:
        print("Connection Failed", e)
        return None

connect_to_db()