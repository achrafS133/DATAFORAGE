"""View sample AI-generated data from database."""
import sqlite3

print("=" * 60)
print("🔍 SAMPLE AI-GENERATED DATA FROM DATAFORGE")
print("=" * 60)

conn = sqlite3.connect("dataforge.db")
cur = conn.cursor()

# Show users with AI-generated bios
print("\n📋 USERS (showing bio field - AI generated):")
print("-" * 50)
cur.execute("SELECT name, email, bio FROM users LIMIT 3")
for row in cur.fetchall():
    print(f"Name: {row[0]}")
    print(f"Email: {row[1]}")
    print(f"Bio: {row[2]}")
    print("-" * 50)

# Show products with AI-generated descriptions
print("\n📦 PRODUCTS (showing description field - AI generated):")
print("-" * 50)
cur.execute("SELECT name, description, price FROM products LIMIT 3")
for row in cur.fetchall():
    print(f"Name: {row[0]}")
    print(f"Description: {row[1]}")
    print(f"Price: ${row[2]}")
    print("-" * 50)

# Show reviews with AI-generated comments
print("\n⭐ REVIEWS (showing comment field - AI generated):")
print("-" * 50)
cur.execute("SELECT comment, rating FROM reviews LIMIT 3")
for row in cur.fetchall():
    print(f"Comment: {row[0]}")
    print(f"Rating: {'⭐' * (row[1] or 3)}")
    print("-" * 50)

# Show stats
print("\n📊 DATABASE STATS:")
for table in ['users', 'products', 'orders', 'reviews']:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"  {table}: {count} rows")

conn.close()
print("\n✅ Done!")
