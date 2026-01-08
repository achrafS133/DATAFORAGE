import requests
import csv
import random
import time
import os
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.theme import Theme

# --- SETUP RICH ---
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "title": "bold magenta",
    "ai": "bold orchid"
})
console = Console(theme=custom_theme)

# --- HELPER DATA ---
CITIES = ["New York", "London", "Paris", "Tokyo", "Berlin", "Sydney", "Toronto", "Dubai", "Singapore", "Mumbai"]
NAMES = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Prince", "Ethan Hunt", "Fiona Gallagher", "George Costanza", "Hannah Abbott", "Ian Wright", "Julia Roberts"]
GENDERS = ["Male", "Female", "Non-binary", "Other"]
DEPARTMENTS = ["Cardiology", "ER", "Neurology", "Pediatrics", "Oncology", "Orthopedics"]
DIAGNOSES = ["Hypertension", "Flu", "Migraine", "Fracture", "Diabetes", "Asthma"]
STATUSES = ["Paid", "Rejected", "Pending"]
ACCOUNT_TYPES = ["Savings", "Current", "Business"]
TRANSACTION_TYPES = ["Transfer", "Withdrawal", "Deposit", "Payment"]
SENSOR_TYPES = ["Temperature", "Pressure", "Vibration", "Humidity"]
ZONES = ["Zone A", "Zone B", "Zone C", "Zone D"]
MAJORS = ["CS", "Math", "Physics", "Chemistry", "Biology", "Literature"]
COURSES = ["Big Data", "Algorithms", "SQL", "Quantum Mechanics", "Genetics", "Calculus"]
PRODUCTS = ["Laptop", "Smartphone", "Headphones", "Monitor", "Keyboard", "Mouse"]

# --- CONSTANTS ---
PROGRESS_TEXT = "[progress.description]{task.description}"
EXPORT_DIR = "exports"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen"
AI_MODE = False

def get_ai_text(column, context=""):
    """Fetch data from Ollama if AI_MODE is on."""
    if not AI_MODE:
        return None
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Generate a single realistic {column} for {context}. Return ONLY the value, no extra text.",
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", "").strip().strip('"')
    except Exception:
        return None
    return None

def get_random_date(days_back=365):
    """Generates a random date within the last n days."""
    random_days = random.randint(0, days_back)
    return (datetime.now() - timedelta(days=random_days)).strftime("%Y-%m-%d %H:%M:%S")

def save_csv(filename, headers, data, subfolder=""):
    """Utility to save data to CSV in a domain-specific subfolder."""
    folder = os.path.join(EXPORT_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

# --- GENERATION FUNCTIONS ---

def generate_ecommerce_data(num_rows):
    sub = "ecommerce"
    with Progress(SpinnerColumn(), TextColumn(PROGRESS_TEXT), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[🛒] Generating E-commerce Data...", total=2)
        
        # AI Mode logic for product names
        users = [[i, random.choice(NAMES), f"user{i}@example.com", random.choice(CITIES), get_random_date(730)] for i in range(1, num_rows + 1)]
        save_csv("users.csv", ["UserID", "Name", "Email", "City", "SignupDate"], users, sub)
        progress.advance(task)
        
        orders = []
        for i in range(1, num_rows + 1):
            product = get_ai_text("e-commerce product name", "an online store") or random.choice(PRODUCTS)
            orders.append([1000 + i, random.randint(1, num_rows), product, random.randint(1, 5), round(random.uniform(10.0, 1000.0), 2), get_random_date(30)])
        save_csv("orders.csv", ["OrderID", "UserID", "Product", "Quantity", "Price", "OrderDate"], orders, sub)
        progress.advance(task)
    
    console.print(f"[success]✅ Created {num_rows} rows in {EXPORT_DIR}/{sub}/[/success]")

def generate_healthcare_data(num_rows):
    sub = "healthcare"
    with Progress(SpinnerColumn(), TextColumn(PROGRESS_TEXT), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[🏥] Generating Healthcare Data...", total=2)
        
        patient_ids = [f"PAT-{100+i}" for i in range(num_rows)]
        patients = [[pid, random.randint(1, 95), random.choice(GENDERS), random.choice(CITIES)] for pid in patient_ids]
        save_csv("patients.csv", ["PatientID", "Age", "Gender", "City"], patients, sub)
        progress.advance(task)
        
        encounters = []
        for i in range(1, num_rows + 1):
            dept = random.choice(DEPARTMENTS)
            diag = get_ai_text("medical diagnosis", f"the {dept} department") or random.choice(DIAGNOSES)
            encounters.append([f"ENC-{1000+i}", random.choice(patient_ids), dept, diag, round(random.uniform(50.0, 5000.0), 2), random.choice(STATUSES), get_random_date(180)])
        save_csv("encounters.csv", ["EncounterID", "PatientID", "Department", "Diagnosis", "Cost", "Status", "Date"], encounters, sub)
        progress.advance(task)

    console.print(f"[success]✅ Created {num_rows} rows in {EXPORT_DIR}/{sub}/[/success]")

def generate_finance_data(num_rows):
    sub = "finance"
    with Progress(SpinnerColumn(), TextColumn(PROGRESS_TEXT), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[💰] Generating Finance Data...", total=2)
        
        account_ids = [f"ACC-{100+i}" for i in range(num_rows)]
        accounts = [[aid, random.choice(NAMES), round(random.uniform(100.0, 100000.0), 2), random.choice(ACCOUNT_TYPES)] for aid in account_ids]
        save_csv("accounts.csv", ["AccountID", "CustomerName", "Balance", "Type"], accounts, sub)
        progress.advance(task)
        
        transactions = []
        for i in range(1, num_rows + 1):
            is_fraud = 1 if random.random() < 0.05 else 0
            amount = round(random.uniform(1.0, 5000.0), 2)
            if random.choice([True, False]): amount = -amount
            transactions.append([f"TRX-{5000+i}", random.choice(account_ids), amount, random.choice(TRANSACTION_TYPES), get_random_date(90), is_fraud])
        save_csv("transactions.csv", ["TransID", "AccountID", "Amount", "Type", "Date", "IsFraud"], transactions, sub)
        progress.advance(task)

    console.print(f"[success]✅ Created {num_rows} rows in {EXPORT_DIR}/{sub}/[/success]")

def generate_iot_data(num_rows):
    sub = "iot"
    with Progress(SpinnerColumn(), TextColumn(PROGRESS_TEXT), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[🏭] Generating IoT Data...", total=2)
        
        sensor_ids = [f"SENS-{100+i}" for i in range(num_rows)]
        sensors = []
        for sid in sensor_ids:
            loc = get_ai_text("industrial location name", "a manufacturing plant") or random.choice(ZONES)
            sensors.append([sid, random.choice(SENSOR_TYPES), loc])
        save_csv("sensors.csv", ["SensorID", "Type", "Location"], sensors, sub)
        progress.advance(task)
        
        readings = []
        base_time = datetime.now() - timedelta(hours=num_rows)
        for i in range(1, num_rows + 1):
            sid = random.choice(sensor_ids)
            timestamp = (base_time + timedelta(minutes=i*10)).strftime("%Y-%m-%d %H:%M:%S")
            unit = "C" if "Temp" in sid else "Pa"
            readings.append([f"READ-{10000+i}", sid, timestamp, round(random.uniform(-10.0, 100.0), 2), unit])
        save_csv("readings.csv", ["ReadingID", "SensorID", "Timestamp", "Value", "Unit"], readings, sub)
        progress.advance(task)

    console.print(f"[success]✅ Created {num_rows} rows in {EXPORT_DIR}/{sub}/[/success]")

def generate_education_data(num_rows):
    sub = "education"
    with Progress(SpinnerColumn(), TextColumn(PROGRESS_TEXT), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[🎓] Generating Education Data...", total=2)
        
        student_ids = [f"STU-{100+i}" for i in range(num_rows)]
        students = [[sid, random.choice(NAMES), random.choice(MAJORS), f"student_{sid.lower()}@university.edu"] for sid in student_ids]
        save_csv("students.csv", ["StudentID", "Name", "Major", "Email"], students, sub)
        progress.advance(task)
        
        grades = []
        for i in range(1, num_rows + 1):
            course = get_ai_text("university course title", "a computer science or physics curriculum") or random.choice(COURSES)
            grades.append([f"GRD-{2000+i}", random.choice(student_ids), course, random.randint(0, 20), get_random_date(120)])
        save_csv("grades.csv", ["GradeID", "StudentID", "Course", "Score", "ExamDate"], grades, sub)
        progress.advance(task)

    console.print(f"[success]✅ Created {num_rows} rows in {EXPORT_DIR}/{sub}/[/success]")

def handle_generation(choice, rows):
    """Router for generation modes."""
    modes = {
        '1': generate_ecommerce_data,
        '2': generate_healthcare_data,
        '3': generate_finance_data,
        '4': generate_iot_data,
        '5': generate_education_data
    }
    if choice in modes:
        modes[choice](rows)

# --- MAIN ---

def main():
    global AI_MODE
    console.clear()
    
    while True:
        ai_status = "[bold green]ON (Qwen)[/bold green]" if AI_MODE else "[bold red]OFF[/bold red]"
        console.print(Panel.fit(
            f"[title]  🌌 UNIVERSAL DATA GENERATOR V2.0  [/title]\n"
            f"[info]The ultimate cross-industry dataset architect[/info]\n"
            f"[dim]AI Generation Mode:[/dim] {ai_status}",
            border_style="orchid" if AI_MODE else "magenta", padding=(1, 5)
        ))

        menu_table = Table(show_header=True, header_style="bold blue", box=None)
        menu_table.add_column("ID", style="dim", width=4)
        menu_table.add_column("Generation Mode", style="cyan")
        
        menu_table.add_row("1", "🛒 [bold]E-commerce Mode[/bold]")
        menu_table.add_row("2", "🏥 [bold]Healthcare Mode[/bold]")
        menu_table.add_row("3", "💰 [bold]Finance Mode[/bold]")
        menu_table.add_row("4", "🏭 [bold]IoT Mode[/bold]")
        menu_table.add_row("5", "🎓 [bold]Education Mode[/bold]")
        menu_table.add_row("a", "[ai]Toggle AI Mode (Ollama Qwen)[/ai]")
        menu_table.add_row("q", "❌ [bold red]Exit[/bold red]")
        
        console.print(menu_table)
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "a", "q"], default="1")
        
        if choice == 'q':
            console.print("[warning]Shutting down architect. Goodbye![/warning]")
            break
        
        if choice == 'a':
            AI_MODE = not AI_MODE
            console.clear()
            continue
            
        rows = IntPrompt.ask("Number of rows to generate", default=10)
        if rows > 0:
            handle_generation(choice, rows)
            input("\nPress Enter to return to menu...")
        else:
            console.print("[error]Please enter a positive integer.[/error]")
            time.sleep(1)
            
        console.clear()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[warning]Aborted by user.[/warning]")
