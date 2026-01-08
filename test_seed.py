"""Quick test to verify seeding works directly without TUI."""
import sys
sys.path.insert(0, '.')

from core.db_connector import DBConnector
from core.schema_parser import SchemaParser
from core.generator import DataGenerator
import yaml

# Load config
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

print("Connecting to database...")
db = DBConnector(config)
print("Connected!")

print("\nTables found:", db.fetch_tables())

print("\nParsing schema...")
parser = SchemaParser(db)
sorted_tables = parser.build_dependency_graph()
print("Sorted tables:", sorted_tables)

print("\nStarting seeding...")
generator = DataGenerator(db, config)

for table in sorted_tables:
    print(f"  Seeding {table}...")
    try:
        generator.seed_table(table, 10)  # Just 10 rows for quick test
        print(f"  ✓ {table} done!")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nVerifying row counts...")
stats = parser.get_table_stats()
for table, count in stats.items():
    print(f"  {table}: {count} rows")

print("\nDone!")
