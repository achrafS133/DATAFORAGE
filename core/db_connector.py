import sqlite3
import os

class DBConnector:
    def __init__(self, config):
        self.config = config.get('database', {})
        # Use SQLite database file in the project directory
        self.db_path = 'dataforge.db'
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with sample tables."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            # Create sample tables for demo
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    bio TEXT,
                    created_at TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    price REAL,
                    created_at TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    order_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    comment TEXT,
                    rating INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')
            conn.commit()

    def get_connection(self):
        """Simple connection factory."""
        return sqlite3.connect(self.db_path)

    def bulk_insert(self, table_name, columns, data_chunk):
        """
        Bulk insert using executemany for SQLite.
        data_chunk: list of tuples
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                placeholders = ', '.join(['?' for _ in columns])
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                cur.executemany(query, data_chunk)
                conn.commit()
                return len(data_chunk)
        except Exception as e:
            print(f"Error inserting into {table_name}: {e}")
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
