import psycopg
import os
from dotenv import load_dotenv

load_dotenv()


try:
    conn = psycopg.connect(
        host = os.getenv('DB_HOST'),
        dbname = "mydb",
        user = "postgres",
        password = os.getenv('DB_PASSWORD'),
        port = 5432,
        sslmode = "require",
        connect_timeout = 10
    )
    print("Connection Successful")
    conn.close()

except Exception as e:
    print("Connection Failed")

# cursor = conn.cursor()
# cursor.execute("SELECT version();")

# if cursor:
#     print("connection worked!")