import networkx as nx
from core.db_connector import DBConnector

class SchemaParser:
    def __init__(self, db_connector: DBConnector):
        self.db = db_connector
        self.graph = nx.DiGraph()

    def build_dependency_graph(self):
        """
        Analyzes FK constraints to build a table dependency graph.
        Returns a topologically sorted list of tables.
        """
        # Get all tables
        tables = self.db.fetch_tables()
        self.graph.add_nodes_from(tables)

        # For SQLite, we need to query each table's foreign keys separately
        for table in tables:
            try:
                fk_query = f"PRAGMA foreign_key_list({table});"
                fk_relations = self.db.execute_query(fk_query)
                if fk_relations:
                    for fk in fk_relations:
                        parent_table = fk[2]  # 'table' column in PRAGMA result
                        if parent_table != table:  # Ignore self-referencing
                            self.graph.add_edge(parent_table, table)  # Parent -> Child
            except Exception as e:
                print(f"Error parsing FK for {table}: {e}")

        return list(nx.topological_sort(self.graph))

    def get_table_columns(self, table_name):
        """Returns list of (column_name, data_type, is_nullable) for a table."""
        query = f"PRAGMA table_info({table_name});"
        result = self.db.execute_query(query)
        # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
        columns = []
        if result:
            for row in result:
                col_name = row[1]
                col_type = row[2].lower() if row[2] else 'text'
                is_nullable = 'YES' if row[3] == 0 else 'NO'
                # Skip auto-increment primary keys
                if row[5] == 1 and 'int' in col_type:
                    continue
                columns.append((col_name, col_type, is_nullable))
        return columns

    def get_table_stats(self):
        """Returns a dict {table_name: row_count}."""
        stats = {}
        for node in self.graph.nodes:
            try:
                res = self.db.execute_query(f"SELECT COUNT(*) FROM {node}")
                if res:
                    stats[node] = res[0][0]
            except Exception:
                stats[node] = 0
        return stats
