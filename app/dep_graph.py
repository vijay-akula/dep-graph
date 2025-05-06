import json
import os
from pyvis.network import Network
import networkx as nx

class DependencyGraph:
    def __init__(self, dependency_dict):
        self.graph = nx.DiGraph()
        self.dependency_dict = dependency_dict
        self.status = {}  # file_name -> 'done' | 'eligible' | 'pending'

        self._build_graph()
        self._initialize_status()

    def _build_graph(self):
        for file, deps in self.dependency_dict.items():
            for dep in deps:
                self.graph.add_edge(dep, file)  # dependency → file
            if not deps:
                self.graph.add_node(file)

    def _initialize_status(self):
        for node in self.graph.nodes:
            if all(self.status.get(pred, 'done') == 'done' for pred in self.graph.predecessors(node)):
                self.status[node] = 'eligible'
            else:
                self.status[node] = 'pending'

    def mark_done(self, node):
        if node not in self.graph.nodes:
            print(f"{node} not in graph")
            return
        self.status[node] = 'done'
        for succ in self.graph.successors(node):
            if all(self.status.get(pred, 'done') == 'done' for pred in self.graph.predecessors(succ)):
                if self.status[succ] != 'done':
                    self.status[succ] = 'eligible'

    def show_graph(self, output_html="dependency_graph.html"):
        net = Network(height='1000px', width='100%', directed=True, notebook=False)

        # Set physics options to make nodes closer together
        net.set_options(json.dumps({
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -5000,
                    "centralGravity": 0.2,
                    "springLength": 80,
                    "springConstant": 0.04,
                    "damping": 0.09,
                    "avoidOverlap": 0.1
                },
                "solver": "barnesHut",
                "stabilization": {
                    "iterations": 150
                }
            }
        }))

        # Colors for node statuses
        color_map = {
            'done': 'green',
            'eligible': 'orange',
            'pending': 'gray'
        }

        # Perform topological sort to ensure root-to-leaf layout
        topological_order = list(nx.topological_sort(self.graph))

        # Adding nodes and edges
        for node in topological_order:
            status = self.status.get(node, 'pending')
            net.add_node(node, label=node, color=color_map[status], title=f"File: {node}<br>Status: {status}")

        for src, dst in self.graph.edges:
            net.add_edge(src, dst)

        # Adding a search feature with filtering by status
        search_script = """
        <div style="position: fixed; top: 10px; left: 10px; z-index: 999;">
            <input id="searchBox" type="text" placeholder="Search node..." 
                   style="padding: 6px; font-size: 14px; width: 200px;">
            <button onclick="searchNode()" style="padding: 6px;">Search</button>
            <select id="filterStatus" style="padding: 6px; font-size: 14px;">
                <option value="all">All</option>
                <option value="done">Done</option>
                <option value="eligible">Eligible</option>
                <option value="pending">Pending</option>
            </select>
        </div>
        <script>
            function searchNode() {
                const val = document.getElementById('searchBox').value.trim().toLowerCase();
                const statusFilter = document.getElementById('filterStatus').value;
                const allIds = nodes.getIds();
                const matches = allIds.filter(id => id.toLowerCase().includes(val));

                if (matches.length === 0) {
                    alert('Node not found.');
                    return;
                }

                // Highlight nodes based on status
                nodes.forEach((node) => {
                    if (statusFilter === 'all' || node.color.background === statusFilter) {
                        const originalColor = node.color?.background || node.color || '#cccccc';
                        nodes.update({ id: node.id, color: { background: originalColor } });
                    }
                });

                const nodeId = matches[0];

                // Highlight the searched node
                nodes.update({
                    id: nodeId,
                    color: {
                        background: '#FFD700',
                        border: '#FF0000',
                        highlight: { background: '#FFD700', border: '#FF0000' }
                    }
                });

                network.selectNodes([nodeId]);
                network.focus(nodeId, { scale: 1.8, animation: true });

                document.getElementById('mynetwork').scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        </script>
        """

        # Temporary HTML generation for pyvis
        tmp_path = "_temp_graph.html"
        net.save_graph(tmp_path)

        # Modify the generated HTML to include the search bar
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html = f.read()

        html = html.replace("</body>", search_script + "\n</body>")

        # Saving final HTML file
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html)

        os.remove(tmp_path)
        print(f"Graph saved to {output_html}. Open it in a browser to interact.")

    def expand_node(self, node_name):
        """Expands the given node to show its dependencies and dependents."""
        dependencies = list(self.graph.predecessors(node_name))
        dependents = list(self.graph.successors(node_name))
        return dependencies, dependents

# Sample dependency dictionary
dependency_dict = {
    "auth_service.py": ["auth_repo.py", "token_util.py"],
    "auth_repo.py": ["db_connector.py"],
    "token_util.py": [],
    "db_connector.py": [],
    "user_service.py": ["auth_service.py", "user_repo.py"],
    "user_repo.py": ["db_connector.py"],
    "payment_service.py": ["user_service.py", "payment_gateway.py"],
    "payment_gateway.py": ["network_util.py"],
    "network_util.py": [],
    "reporting_service.py": ["user_service.py", "payment_service.py"],
    "ui_dashboard.py": ["reporting_service.py"]
}

# Example usage
if __name__ == "__main__":
    dg = DependencyGraph(dependency_dict)

    # Mark initial nodes as done
    dg.mark_done("auth_repo.py")
    dg.mark_done("db_connector.py")

    # Show the graph
    dg.show_graph("intellij_like_dependency_graph.html")
