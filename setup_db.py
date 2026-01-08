import psycopg

# Connect to default postgres database to create our database
try:
    conn = psycopg.connect("dbname=postgres user=postgres password=password host=localhost port=5432")
    conn.autocommit = True
    cur = conn.cursor()
    
    # Create database if not exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'dataforge_db'")
    if not cur.fetchone():
        cur.execute("CREATE DATABASE dataforge_db")
        print("Database 'dataforge_db' created successfully!")
    else:
        print("Database 'dataforge_db' already exists.")
    
    cur.close()
    conn.close()
    
    # Now connect to our database and create tables
    conn = psycopg.connect("dbname=dataforge_db user=postgres password=password host=localhost port=5432")
    cur = conn.cursor()
    
    # Create tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            description TEXT,
            price DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            product_id INTEGER REFERENCES products(id),
            comment TEXT,
            rating INTEGER
        )
    ''')
    conn.commit()
    print("Tables created successfully: users, products, orders, reviews")
    
    # Verify
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables in database: {tables}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
