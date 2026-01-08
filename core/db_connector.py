import sqlite3
import os

class DBConnector:
    DOMAINS = {
        "E-commerce": [
            "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, city TEXT, signup_date TEXT)",
            "CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL, category TEXT)",
            "CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id INTEGER, quantity INTEGER, order_date TEXT, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(product_id) REFERENCES products(id))"
        ],
        "Healthcare": [
            "CREATE TABLE patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, gender TEXT, city TEXT)",
            "CREATE TABLE encounters (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, department TEXT, diagnosis TEXT, cost REAL, date TEXT, FOREIGN KEY(patient_id) REFERENCES patients(id))"
        ],
        "Finance": [
            "CREATE TABLE accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, balance REAL, type TEXT)",
            "CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, amount REAL, type TEXT, date TEXT, is_fraud INTEGER, FOREIGN KEY(account_id) REFERENCES accounts(id))"
        ],
        "IoT": [
            "CREATE TABLE sensors (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, location TEXT)",
            "CREATE TABLE readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sensor_id INTEGER, timestamp TEXT, value REAL, unit TEXT, FOREIGN KEY(sensor_id) REFERENCES sensors(id))"
        ],
        "Education": [
            "CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, major TEXT, email TEXT)",
            "CREATE TABLE grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, course TEXT, score INTEGER, date TEXT, FOREIGN KEY(student_id) REFERENCES students(id))"
        ]
    }

    def __init__(self, config):
        self.config = config.get('database', {})
        self.db_path = 'dataforge.db'
        # Don't auto-init anymore, let the TUI decide

    def init_domain(self, domain_name):
        """Reset and initialize a specific domain schema."""
        if domain_name not in self.DOMAINS:
            return False
            
        with self.get_connection() as conn:
            cur = conn.cursor()
            # Drop existing tables
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cur.fetchall()]
            for table in tables:
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            
            # Create new schema
            for sql in self.DOMAINS[domain_name]:
                cur.execute(sql)
            conn.commit()
        return True

    def get_connection(self):
        """Simple connection factory."""
        return sqlite3.connect(self.db_path)

    def bulk_insert(self, table_name, columns, data_chunk):
        """
        Bulk insert using executemany for SQLite.
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                placeholders = ', '.join(['?' for _ in columns])
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cur.executemany(query, data_chunk)
                conn.commit()
                return len(data_chunk)
        except Exception:
            return 0
    
    def fetch_tables(self):
        """Retrieve all table names from SQLite."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            return [row[0] for row in cur.fetchall()]

    def execute_query(self, query):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            if cur.description:
                return cur.fetchall()
