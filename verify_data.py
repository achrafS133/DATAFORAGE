import yaml
from core.db_connector import DBConnector

def verify():
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    db = DBConnector({'database': config['database']})
    tables = db.fetch_tables()
    
    print(f"Found {len(tables)} tables.")
    for table in tables:
        count = db.execute_query(f"SELECT COUNT(*) FROM {table}")[0][0]
        print(f"Table '{table}': {count} rows")
        
        # Sample a few rows
        cols = db.execute_query(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
        col_names = [c[0] for c in cols]
        
        print(f"  Columns: {col_names}")
        rows = db.execute_query(f"SELECT * FROM {table} LIMIT 3")
        for row in rows:
            print(f"  - {row}")

if __name__ == "__main__":
    verify()
