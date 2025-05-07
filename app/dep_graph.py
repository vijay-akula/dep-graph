from pyvis.network import Network
import networkx as nx
import json
import os

class DependencyGraph:
    def __init__(self, dependencies, state_file="dep_graph_state.json"):
        self.graph = nx.DiGraph()
        self.dependencies = dependencies
        self.state_file = state_file
        self.statuses = {}  # node -> 'pending' | 'in-progress' | 'done'
        self.load_state()  # Load previous state if available
        self.build_graph()

    def build_graph(self):
        for file, deps in self.dependencies.items():
            self.graph.add_node(file)
            if file not in self.statuses:
                self.statuses[file] = "pending"
            for dep in deps:
                self.graph.add_node(dep)
                self.graph.add_edge(dep, file)  # dep -> file
                if dep not in self.statuses:
                    self.statuses[dep] = "pending"

    def mark_done(self, node):
        if node in self.statuses:
            self.statuses[node] = "done"
            self.save_state()  # Save state after marking a node as done

    def get_eligible_nodes(self):
        eligible = []
        for node in self.graph.nodes:
            if self.statuses[node] != "pending":
                continue
            preds = list(self.graph.predecessors(node))
            if all(self.statuses.get(p, "pending") == "done" for p in preds):
                eligible.append(node)
        return eligible

    def traverse_bottom_up(self):
        return list(nx.topological_sort(self.graph))

    def show_graph(self, output_html="graph.html"):
        net = Network(height="750px", width="100%", directed=True, layout=True)

        color_map = {
            "pending": "gray",
            "in-progress": "orange",
            "done": "green",
            "eligible": "#FFC107"  # amber color
        }

        eligible_nodes = set(self.get_eligible_nodes())

        for node in self.graph.nodes:
            status = self.statuses.get(node, "pending")
            color = color_map.get(status, "gray")
            if status == "pending" and node in eligible_nodes:
                color = color_map["eligible"]
                title = f"{node} - eligible (no pending dependencies)"
            else:
                title = f"{node} - {status}"

            net.add_node(
                node,
                label=node,
                color=color,
                title=title
            )

        for edge in self.graph.edges:
            net.add_edge(edge[0], edge[1], arrows="to")

        # Enable save and load buttons in HTML
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed",
              "nodeSpacing": 200,
              "treeSpacing": 300,
              "blockShifting": true,
              "edgeMinimization": true,
              "parentCentralization": true
            },
            "improvedLayout": true
          },
          "physics": {
            "enabled": false
          },
          "interaction": {
            "navigationButtons": true,
            "keyboard": {
              "enabled": true,
              "speed": {
                "x": 10,
                "y": 10,
                "zoom": 0.02
              },
              "bindToWindow": true
            },
            "tooltipDelay": 200,
            "hover": true,
            "zoomView": true,
            "dragView": true
          },
          "manipulation": {
            "enabled": false
          },
          "configure": {
            "enabled": true
          }
        }
        """)

        net.write_html(output_html)

    def save_state(self):
        """Save the current node statuses to a JSON file."""
        with open(self.state_file, "w") as f:
            json.dump(self.statuses, f, indent=4)

    def load_state(self):
        """Load the node statuses from the state file, if it exists."""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                self.statuses = json.load(f)

if __name__ == "__main__":
    dependencies = {
        "auth_service.py": ["auth_repo.py", "db_connector.py"],
        "payment_service.py": ["payment_repo.py", "db_connector.py"],
        "order_service.py": ["order_repo.py", "payment_service.py", "auth_service.py"],
        "main.py": ["order_service.py"],
        "auth_repo.py": [],
        "payment_repo.py": ["db_connector.py"],
        "order_repo.py": ["db_connector.py"],
        "db_connector.py": []
    }

    dg = DependencyGraph(dependencies)

    # Mark initial completed nodes
    dg.mark_done("auth_repo.py")
    dg.mark_done("db_connector.py")

    print("Eligible nodes:", dg.get_eligible_nodes())
    print("Bottom-up order:", dg.traverse_bottom_up())

    # Show graph with the current state
    dg.show_graph("intellij_like_dependency_graph.html")

    # You can also manually save/load states if needed
    # dg.save_state()  # Manually save
    # dg.load_state()  # Manually load if needed

