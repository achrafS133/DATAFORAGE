"""Seed all tables with data."""
import sys
sys.path.insert(0, '.')

from core.db_connector import DBConnector
from core.schema_parser import SchemaParser
from core.generator import DataGenerator
import yaml

# Load config - disable AI for faster seeding
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

# Override to disable AI for speed
config['generation']['use_ai_mode'] = False
config['generation']['batch_size'] = 50

print("Connecting to database...")
db = DBConnector(config)
print("Connected!")

print("\nParsing schema...")
parser = SchemaParser(db)
sorted_tables = parser.build_dependency_graph()
print("Tables:", sorted_tables)

print("\n🔥 Seeding ALL tables (100 rows each)...")
generator = DataGenerator(db, config)

for table in sorted_tables:
    print(f"  Seeding {table}...", end=" ")
    try:
        generator.seed_table(table, 100)
        print("✓ Done!")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n📊 Final row counts:")
stats = parser.get_table_stats()
for table, count in stats.items():
    print(f"  {table}: {count} rows")

print("\n✅ All tables seeded!")
