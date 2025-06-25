import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

print("=== DEBUGGING INFO ===")
print(f"DB_HOST: '{os.getenv('DB_HOST')}'")
print(f"DB_PASSWORD exists: {os.getenv('DB_PASSWORD') is not None}")
print(f"DB_PASSWORD length: {len(os.getenv('DB_PASSWORD') or '')}")
print("========================")

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