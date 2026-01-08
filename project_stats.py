import os
import sqlite3
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def get_db_stats():
    db_path = "dataforge.db"
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
    
    stats = []
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats.append((table, count))
    
    conn.close()
    return stats

def get_export_stats():
    export_dir = "exports"
    if not os.path.exists(export_dir):
        return []
    
    files = os.listdir(export_dir)
    return [(f, os.path.getsize(os.path.join(export_dir, f))) for f in files]

def main():
    console.clear()
    console.print(Panel.fit("[bold cyan]📊 DATAFORAGE PROJECT STATUS[/bold cyan]", border_style="blue"))
    
    # DB Stats
    db_stats = get_db_stats()
    if db_stats:
        table = Table(title="Database Inventory", show_header=True, header_style="bold green")
        table.add_column("Table Name", style="cyan")
        table.add_column("Row Count", justify="right", style="magenta")
        
        for name, count in db_stats:
            table.add_row(name, str(count))
        
        console.print(table)
    else:
        console.print("[yellow]No database found.[/yellow]")

    # Export Stats
    export_stats = get_export_stats()
    if export_stats:
        table = Table(title="Generated Exports", show_header=True, header_style="bold yellow")
        table.add_column("File Name", style="cyan")
        table.add_column("Size (bytes)", justify="right", style="magenta")
        
        for name, size in export_stats:
            table.add_row(name, str(size))
        
        console.print(table)
    else:
        console.print("[yellow]No exports found.[/yellow]")

    console.print(Panel.fit(
        "[dim]Quick Tip: Run 'python run.bat' for the main menu[/dim]",
        border_style="dim"
    ))

if __name__ == "__main__":
    main()
