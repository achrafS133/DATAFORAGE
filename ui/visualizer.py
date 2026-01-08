from rich.tree import Tree
from rich.text import Text
import networkx as nx

class SchemaVisualizer:
    def __init__(self, dependency_graph_nx: nx.DiGraph):
        self.graph = dependency_graph_nx

    def generate_tree(self, stats=None):
        """
        Generates a Rich Tree object representing the schema hierarchy.
        stats: Dictionary of {table_name: row_count}
        """
        # Find root nodes (indegree 0) - tables with no foreign keys (or circular deps broken)
        roots = [n for n, d in self.graph.in_degree() if d == 0]
        
        if not roots and len(self.graph.nodes) > 0:
            # Cycle detected or no clear root, pick arbitrarily
            roots = [list(self.graph.nodes)[0]]

        main_tree = Tree("Database Schema", guide_style="bold bright_magenta")

        visited = set()

        def add_children(node, tree_branch):
            visited.add(node)
            
            # Label
            label_text = node
            if stats and node in stats:
                label_text += f" [dim]({stats[node]} rows)[/dim]"
            
            # Children
            children = list(self.graph.successors(node))
            
            for child in children:
                if child not in visited:
                     child_label = child
                     if stats and child in stats:
                         child_label += f" [dim]({stats[child]} rows)[/dim]"
                     
                     branch = tree_branch.add(Text.from_markup(f"[green]{child_label}[/green]"))
                     add_children(child, branch)
                else:
                    # Recursive link or already visited
                    tree_branch.add(Text(f"{child} (Revisited)", style="dim yellow"))

        for root in roots:
            root_label = root
            if stats and root in stats:
                root_label += f" [dim]({stats[root]} rows)[/dim]"
                
            root_branch = main_tree.add(Text.from_markup(f"[bold green]{root_label}[/bold green]"))
            add_children(root, root_branch)
            
        return main_tree
