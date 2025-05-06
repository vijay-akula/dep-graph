from pyvis.network import Network
import networkx as nx
import json

class DependencyGraph:
    def __init__(self, dependencies):
        self.graph = nx.DiGraph()
        self.dependencies = dependencies
        self.statuses = {}  # node -> 'pending' | 'in-progress' | 'done'
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
            "done": "green"
        }

        for node in self.graph.nodes:
            status = self.statuses.get(node, "pending")
            net.add_node(
                node,
                label=node,
                color=color_map.get(status, "gray"),
                title=f"{node} - {status}"
            )

        for edge in self.graph.edges:
            net.add_edge(edge[0], edge[1], arrows="to")

        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed"
            }
          },
          "physics": {
            "enabled": true,
            "hierarchicalRepulsion": {
              "centralGravity": 0.0,
              "springLength": 80,
              "springConstant": 0.01,
              "nodeDistance": 100,
              "damping": 0.09
            },
            "solver": "hierarchicalRepulsion"
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

if __name__ == "__main__":
    dependencies = {
        "auth_service.py": ["auth_repo.py", "db_connector.py"],
        "payment_service.py": ["payment_repo.py", "db_connector.py"],
        "order_service.py": ["order_repo.py", "payment_service.py", "auth_service.py"],
        "main.py": ["order_service.py"],
        "auth_repo.py": [],
        "payment_repo.py": [],
        "order_repo.py": [],
        "db_connector.py": []
    }

    dg = DependencyGraph(dependencies)

    # Mark initial completed nodes
    dg.mark_done("auth_repo.py")
    dg.mark_done("db_connector.py")
    dg.mark_done("payment_repo.py")

    print("Eligible nodes:", dg.get_eligible_nodes())
    print("Bottom-up order:", dg.traverse_bottom_up())

    dg.show_graph("intellij_like_dependency_graph.html")
