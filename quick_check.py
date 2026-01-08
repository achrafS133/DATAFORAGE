import psycopg
import time

print("Script started.")
try:
    print("Attempting connection...")
    conn = psycopg.connect("dbname=dataforge_db user=postgres password=password host=localhost port=5432", connect_timeout=5)
    print("Connected.")
    with conn.cursor() as cur:
        print("Executing query...")
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
        print(f"Result: {cur.fetchone()}")
    conn.close()
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
