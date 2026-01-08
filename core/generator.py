import multiprocessing
from faker import Faker
import random
import time

from core.ai_agent import AIAgent

fake = Faker()

def generate_row(columns_metadata, ai_config=None):
    """
    Generates a single row of data based on column types.
    columns_metadata: List of (name, type, is_nullable)
    ai_config: Dictionary containing AI settings if enabled
    """
    ai_agent = None
    if ai_config and ai_config.get('enabled'):
         ai_agent = AIAgent({'ai': ai_config, 'generation': {'use_ai_mode': True}})

    row = []
    for col_name, col_type, is_nullable in columns_metadata:
        val = None
        col_lower = col_name.lower()
        type_lower = col_type.lower() if col_type else 'text'
        
        # AI Attempt for specific fields or any descriptive text
        if ai_agent and ('text' in type_lower or 'varchar' in type_lower or 'char' in type_lower):
            descriptive_fields = ['desc', 'bio', 'review', 'comment', 'diagnosis', 'major', 'course', 'content']
            if any(x in col_lower for x in descriptive_fields):
                val = ai_agent.generate_text("table", col_name, context_hint=f"Value for {col_name}")

        if val is None:
            # Domain-Specific Logic
            if 'diagnosis' in col_lower:
                val = random.choice(["Hypertension", "Flu", "Migraine", "Fracture", "Diabetes", "Asthma", "Anxiety"])
            elif 'department' in col_lower:
                val = random.choice(["Cardiology", "ER", "Neurology", "Pediatrics", "Oncology", "Orthopedics"])
            elif 'major' in col_lower:
                val = random.choice(["Computer Science", "Mechanical Engineering", "Psychology", "Economics", "History"])
            elif 'course' in col_lower:
                val = random.choice(["Big Data", "Algorithms", "Calculus", "Quantum Mechanics", "Genetics"])
            elif 'unit' in col_lower:
                val = random.choice(["°C", "Pa", "kW", "m/s", "Lux", "%RH"])
            
            # Numeric Rules
            elif 'int' in type_lower or 'integer' in type_lower:
                if 'age' in col_lower:
                    val = random.randint(1, 95)
                elif 'score' in col_lower:
                    val = random.randint(0, 100)
                elif 'is_fraud' in col_lower:
                    val = 1 if random.random() < 0.05 else 0
                elif any(x in col_lower for x in ['user_id', 'customer_id', 'patient_id', 'account_id', 'sensor_id', 'student_id']):
                    val = random.randint(1, 100)
                elif 'quantity' in col_lower:
                    val = random.randint(1, 10)
                elif 'rating' in col_lower:
                    val = random.randint(1, 5)
                else:
                    val = random.randint(1, 1000)
            
            # Currency / Float Rules
            elif any(x in type_lower for x in ['real', 'float', 'double', 'decimal']):
                if any(x in col_lower for x in ['price', 'cost', 'amount', 'balance']):
                    val = round(random.uniform(10.0, 5000.0), 2)
                elif 'value' in col_lower:
                    val = round(random.uniform(-20.0, 150.0), 2)
                else:
                    val = round(random.uniform(0, 100), 2)
            
            # String Rules
            elif any(x in type_lower for x in ['char', 'text']):
                if 'email' in col_lower:
                    val = fake.email()
                elif 'name' in col_lower or 'owner' in col_lower:
                    val = fake.name()
                elif 'city' in col_lower:
                    val = fake.city()
                elif 'type' in col_lower:
                    val = random.choice(["Standard", "Premium", "Legacy", "Experimental"])
                elif 'location' in col_lower:
                    val = random.choice(["Zone A", "Zone B", "Warehouse", "Lab", "Global"])
                else:
                    val = fake.sentence(nb_words=6)
            
            # Temporal Rules
            elif 'date' in type_lower or 'time' in type_lower:
                val = str(fake.date_time_this_decade())
            
            # Boolean
            elif 'bool' in type_lower:
                val = random.choice([True, False])
            
            else:
                val = "DataForge_Gen"
        
        row.append(val)
    return tuple(row)

def worker_generate_chunk(chunk_size, columns_metadata, queue, ai_config=None):
    """
    Worker function to generate a batch of data.
    """
    chunk = []
    for _ in range(chunk_size):
        chunk.append(generate_row(columns_metadata, ai_config))
    queue.put(chunk)

class DataGenerator:
    def __init__(self, db_connector, config):
        self.db = db_connector
        self.config = config # Store full config
        self.batch_size = config['generation']['batch_size']
        self.num_workers = config['generation']['workers']

    def seed_table(self, table_name, total_rows):
        """
        Orchestrates the seeding process.
        """
        # Get schema using SQLite PRAGMA
        raw_columns = self.db.execute_query(f"PRAGMA table_info({table_name})")
        if not raw_columns:
            print(f"Table {table_name} not found.")
            return
        
        # Convert PRAGMA result to (name, type, is_nullable) format
        # PRAGMA returns: (cid, name, type, notnull, dflt_value, pk)
        columns_meta = []
        column_names = []
        for row in raw_columns:
            col_name = row[1]
            col_type = (row[2] or 'text').lower()
            is_nullable = 'YES' if row[3] == 0 else 'NO'
            is_pk = row[5] == 1
            # Skip auto-increment primary keys
            if is_pk and 'int' in col_type:
                continue
            columns_meta.append((col_name, col_type, is_nullable))
            column_names.append(col_name)
        
        # Setup Multiprocessing
        manager = multiprocessing.Manager()
        queue = manager.Queue(maxsize=self.num_workers * 2)
        
        pool = multiprocessing.Pool(processes=self.num_workers)
        
        rows_generated = 0
        active_workers = 0
        
        # Prepare AI config for workers
        ai_config = None
        if self.config['generation']['use_ai_mode']:
            ai_config = self.config['ai']
            ai_config['enabled'] = True

        # Start initial workers
        for _ in range(self.num_workers):
            pool.apply_async(worker_generate_chunk, args=(self.batch_size, columns_meta, queue, ai_config))
            active_workers += 1

        start_time = time.time()
        
        while rows_generated < total_rows:
            # Consume from queue
            chunk = queue.get()
            
            # Write to DB
            self.db.bulk_insert(table_name, column_names, chunk)
            rows_generated += len(chunk)
            
            # Schedule next task
            if rows_generated + (active_workers * self.batch_size) < total_rows:
                 pool.apply_async(worker_generate_chunk, args=(self.batch_size, columns_meta, queue, ai_config))
            else:
                active_workers -= 1
                
        pool.close()
        pool.join()
        
        duration = time.time() - start_time
        print(f"Seeded {total_rows} rows in {duration:.2f}s ({total_rows/duration:.0f} rows/s)")
