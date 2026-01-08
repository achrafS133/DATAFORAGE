from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label, Log, DataTable
from textual.containers import Vertical, Container
from rich.text import Text

class TableList(Static):
    """Sidebar to show list of detected tables."""
    
    def __init__(self):
        super().__init__()
        self.tables = []
    
    def compose(self) -> ComposeResult:
        yield ListView(id="table-list-view")

    def add_table(self, table_name: str):
        self.tables.append(table_name)
        list_view = self.query_one("#table-list-view", ListView)
        list_view.append(ListItem(Label(table_name)))

    def remove_table(self, table_name: str):
        if table_name in self.tables:
            self.tables.remove(table_name)
            self._refresh_list()
    
    def clear_tables(self):
        self.tables = []
        list_view = self.query_one("#table-list-view", ListView)
        list_view.clear()

    def _refresh_list(self):
        list_view = self.query_one("#table-list-view", ListView)
        list_view.clear()
        for table in self.tables:
            list_view.append(ListItem(Label(table)))

class VisualizerPanel(Static):
    """Main area for Schema Visualizer or Data Entry details."""
    
    def compose(self) -> ComposeResult:
        yield Label("DATA ENTRY / SCHEMA VISUALIZER", classes="title")
        yield Static(id="visualizer-content", expand=True)

    def update_content(self, content: str):
        self.query_one("#visualizer-content", Static).update(content)

class LogPanel(Static):
    """Bottom panel for logs and progress metrics."""

    def compose(self) -> ComposeResult:
        yield Label("PROGRESS & LOGS", classes="title")
        yield Log(id="activity-log", highlight=True)

    def log_message(self, message: str, level: str = "info"):
        log_widget = self.query_one("#activity-log", Log)
        
        # Color mapping compatible with Rich style
        # We use explicit colors because .tcss classes usually don't apply to rich markup content inside a Log widget easily 
        # unless we use specific tags, but [color] tags are standard.
        style_map = {
            "info": "green",
            "warn": "yellow",
            "error": "red",
            "ai": "cyan"
        }
        
        color = style_map.get(level, "white")
        # Write using markup
        log_widget.write(f"[{color}]> {message}[/{color}]")
