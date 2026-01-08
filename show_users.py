"""Show actual user data from database."""
import sqlite3

conn = sqlite3.connect("dataforge.db")
cur = conn.cursor()

print("=" * 60)
print("👤 SAMPLE USERS FROM DATABASE")
print("=" * 60)

cur.execute("SELECT name, email, bio FROM users LIMIT 5")
users = cur.fetchall()

for i, user in enumerate(users, 1):
    print(f"\n--- User {i} ---")
    print(f"Name:  {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Bio:   {user[2][:100] if user[2] else 'N/A'}...")

# Total count
cur.execute("SELECT COUNT(*) FROM users")
total = cur.fetchone()[0]
print(f"\n📊 Total Users: {total}")

conn.close()
