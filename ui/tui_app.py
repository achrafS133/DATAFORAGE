from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ProgressBar, Label
from textual.containers import Container, Vertical, Horizontal
from textual.worker import Worker
from ui.panels import TableList, VisualizerPanel, LogPanel
from ui.visualizer import SchemaVisualizer
from core.db_connector import DBConnector
from core.schema_parser import SchemaParser
from core.generator import DataGenerator
import yaml
import time

class CompletedTables(Static):
    """Panel showing completed tables."""
    def __init__(self):
        super().__init__()
        self.completed = []
    
    def add_completed(self, table_name, row_count):
        self.completed.append(f"✓ {table_name} ({row_count} rows)")
        self.update("\n".join(self.completed) if self.completed else "(none yet)")
    
    def clear_completed(self):
        self.completed = []
        self.update("(none yet)")

class DataForgeApp(App):
    """The main TUI Application for DataForge."""
    
    CSS_PATH = "styles.tcss"
    TITLE = "DATAFORAGE"
    SUB_TITLE = "From ER-RAHOUTI ACHRAF"

    BINDINGS = [
        ("s", "start_seeding", "Start Seeding"),
        ("d", "show_data", "View Data"),
        ("e", "export_csv", "Export CSV"),
        ("x", "export_sql", "Export SQL"),
        ("r", "reset_db", "Reset DB"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.db_connector = None
        self.schema_parser = None
        self.sorted_tables = []
        self.seeding_active = False
        self.stats = {"rows_added": 0, "start_time": None, "rows_per_sec": 0}

    def load_config(self, config_path="config/settings.yaml"):
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        # Main 3-column layout
        with Container(id="main-container"):
            # Left - Tables Remaining
            with Container(id="table-list-panel", classes="box"):
                yield Label("TABLES REMAINING", classes="panel-title")
                yield TableList()
            
            # Center - Data Entry / Visualizer
            with Container(id="visualizer-panel", classes="box"):
                yield Label("DATA ENTRY", classes="panel-title")
                yield VisualizerPanel()
            
            # Right - Completed Tables
            with Container(id="completed-panel", classes="box"):
                yield Label("COMPLETED TABLES", classes="panel-title")
                yield CompletedTables()
        
        # Progress section
        with Container(id="progress-container"):
            yield Label("Progress", id="progress-title")
            yield Label("Identifying relations", id="progress-label-1")
            yield ProgressBar(total=100, id="progress-1")
            yield Label("Inserting data into tables", id="progress-label-2")
            yield ProgressBar(total=100, id="progress-2")
        
        yield Footer()

    async def on_mount(self) -> None:
        """Called when app starts."""
        # Update footer message
        self.query_one(Footer).styles.height = 2
        
        # Start initialization in background
        self.run_worker(self.initialize_backend, exclusive=True, thread=True)

    def initialize_backend(self):
        """Connects to DB and parses schema."""
        # Update progress
        self.call_from_thread(self.update_progress, 1, 0, "Connecting to database...")
        
        try:
            self.db_connector = DBConnector(self.config)
            self.db_connector.fetch_tables()
            self.call_from_thread(self.update_progress, 1, 50, "Database connected!")
        except Exception as e:
            self.call_from_thread(self.update_progress, 1, 0, f"Connection failed: {e}")
            return

        self.call_from_thread(self.update_progress, 1, 75, "Parsing schema...")
        self.schema_parser = SchemaParser(self.db_connector)
        self.sorted_tables = self.schema_parser.build_dependency_graph()
        
        # Update Table List
        def update_table_list():
            table_list = self.query_one(TableList)
            for table in self.sorted_tables:
                table_list.add_table(table)
        self.call_from_thread(update_table_list)
            
        # Update Visualizer with current data preview
        self.call_from_thread(self.update_progress, 1, 100, "Identifying relations")
        
        visualizer = SchemaVisualizer(self.schema_parser.graph)
        stats = self.schema_parser.get_table_stats()
        tree = visualizer.generate_tree(stats)
        self.call_from_thread(self.query_one(VisualizerPanel).update_content, tree)
        
        self.call_from_thread(self.update_progress, 2, 0, "Ready! Press 's' to start seeding")

    def update_progress(self, bar_num, value, label_text):
        """Update progress bar and label."""
        try:
            progress = self.query_one(f"#progress-{bar_num}", ProgressBar)
            label = self.query_one(f"#progress-label-{bar_num}", Label)
            progress.update(progress=value)
            label.update(label_text)
        except Exception:
            pass

    def action_start_seeding(self):
        """Action to start the seeding process."""
        if not self.sorted_tables:
            return
        if self.seeding_active:
            return
        
        self.seeding_active = True
        self.query_one(CompletedTables).clear_completed()
        self.run_worker(self.run_seeding_process, exclusive=True, thread=True)

    def run_seeding_process(self):
        """Background worker for seeding."""
        generator = DataGenerator(self.db_connector, self.config)
        total_tables = len(self.sorted_tables)
        
        for idx, table in enumerate(self.sorted_tables):
            progress_pct = int((idx / total_tables) * 100)
            self.call_from_thread(self.update_progress, 2, progress_pct, f"Seeding: {table}")
            
            try:
                generator.seed_table(table, 100)  # 100 rows per table
                
                # Get row count
                stats = self.schema_parser.get_table_stats()
                row_count = stats.get(table, 0)
                
                # Add to completed
                self.call_from_thread(self.query_one(CompletedTables).add_completed, table, row_count)
                
                # Remove from remaining
                def remove_table():
                    table_list = self.query_one(TableList)
                    table_list.remove_table(table)
                self.call_from_thread(remove_table)
                
                # Update visualizer
                visualizer = SchemaVisualizer(self.schema_parser.graph)
                tree = visualizer.generate_tree(stats)
                self.call_from_thread(self.query_one(VisualizerPanel).update_content, tree)
                
            except Exception as e:
                self.call_from_thread(self.update_progress, 2, progress_pct, f"Error: {e}")
        
        self.call_from_thread(self.update_progress, 2, 100, "Seeding complete!")
        self.seeding_active = False

    def action_show_data(self):
        """Show sample data from all tables."""
        if not self.db_connector:
            return
        self.run_worker(self.show_data_preview, exclusive=True, thread=True)

    def show_data_preview(self):
        """Display sample data from each table."""
        output_lines = ["[bold cyan]📊 DATA PREVIEW[/bold cyan]\n"]
        
        for table in self.sorted_tables:
            try:
                cols = self.db_connector.execute_query(f"PRAGMA table_info({table})")
                count_result = self.db_connector.execute_query(f"SELECT COUNT(*) FROM {table}")
                count = count_result[0][0] if count_result else 0
                
                output_lines.append(f"\n[bold yellow]📋 {table.upper()}[/bold yellow] ({count} rows)")
                output_lines.append("-" * 40)
                
                rows = self.db_connector.execute_query(f"SELECT * FROM {table} LIMIT 3")
                if rows:
                    for i, row in enumerate(rows, 1):
                        output_lines.append(f"[green]Row {i}:[/green]")
                        for j, col in enumerate(cols):
                            col_name = col[1]
                            val = str(row[j])[:50] if row[j] else "NULL"
                            output_lines.append(f"  {col_name}: {val}")
                else:
                    output_lines.append("  (no data)")
            except Exception as e:
                output_lines.append(f"  Error: {e}")
        
        preview_text = "\n".join(output_lines)
        self.call_from_thread(self.query_one(VisualizerPanel).update_content, preview_text)

    def action_export_csv(self):
        """Export all tables to CSV files."""
        if not self.db_connector:
            return
        self.run_worker(self.export_to_csv, exclusive=True, thread=True)

    def export_to_csv(self):
        """Export tables to CSV files."""
        import csv
        import os
        
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        self.call_from_thread(self.update_progress, 2, 0, "Exporting to CSV...")
        
        for idx, table in enumerate(self.sorted_tables):
            try:
                cols = self.db_connector.execute_query(f"PRAGMA table_info({table})")
                col_names = [c[1] for c in cols]
                rows = self.db_connector.execute_query(f"SELECT * FROM {table}")
                
                filepath = os.path.join(export_dir, f"{table}.csv")
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(col_names)
                    if rows:
                        writer.writerows(rows)
                
                progress = int(((idx + 1) / len(self.sorted_tables)) * 100)
                self.call_from_thread(self.update_progress, 2, progress, f"Exported: {table}.csv")
            except Exception as e:
                self.call_from_thread(self.update_progress, 2, 0, f"Export error: {e}")
        
        self.call_from_thread(self.update_progress, 2, 100, f"Exported to {export_dir}/ folder!")

    def action_export_sql(self):
        """Export all tables to SQL file."""
        if not self.db_connector:
            return
        self.run_worker(self.export_to_sql, exclusive=True, thread=True)

    def export_to_sql(self):
        """Export tables to SQL INSERT statements."""
        import os
        
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, "dataforge_dump.sql")
        
        self.call_from_thread(self.update_progress, 2, 0, "Exporting to SQL...")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("-- DataForge SQL Dump\n")
            f.write(f"-- Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for idx, table in enumerate(self.sorted_tables):
                try:
                    cols = self.db_connector.execute_query(f"PRAGMA table_info({table})")
                    col_names = [c[1] for c in cols]
                    rows = self.db_connector.execute_query(f"SELECT * FROM {table}")
                    
                    f.write(f"\n-- Table: {table}\n")
                    if rows:
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, str):
                                    escaped = val.replace("'", "''")
                                    values.append(f"'{escaped}'")
                                else:
                                    values.append(str(val))
                            cols_str = ", ".join(col_names)
                            vals_str = ", ".join(values)
                            f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});\n")
                    
                    progress = int(((idx + 1) / len(self.sorted_tables)) * 100)
                    self.call_from_thread(self.update_progress, 2, progress, f"SQL: {table}")
                except Exception as e:
                    f.write(f"-- Error exporting {table}: {e}\n")
        
        self.call_from_thread(self.update_progress, 2, 100, f"SQL exported: {filepath}")

    def action_reset_db(self):
        """Reset the database - clear all data."""
        if not self.db_connector:
            return
        self.run_worker(self.reset_database, exclusive=True, thread=True)

    def reset_database(self):
        """Clear all data from tables."""
        self.call_from_thread(self.update_progress, 2, 0, "Resetting database...")
        
        # Reverse order to handle foreign keys
        for table in reversed(self.sorted_tables):
            try:
                self.db_connector.execute_query(f"DELETE FROM {table}")
                self.call_from_thread(self.update_progress, 2, 50, f"Cleared: {table}")
            except Exception as e:
                self.call_from_thread(self.update_progress, 2, 0, f"Error: {e}")
        
        # Refresh visualizer
        stats = self.schema_parser.get_table_stats()
        visualizer = SchemaVisualizer(self.schema_parser.graph)
        tree = visualizer.generate_tree(stats)
        self.call_from_thread(self.query_one(VisualizerPanel).update_content, tree)
        self.call_from_thread(self.query_one(CompletedTables).clear_completed)
        
        self.call_from_thread(self.update_progress, 2, 100, "Database reset complete!")

if __name__ == "__main__":
    app = DataForgeApp()
    app.run()
