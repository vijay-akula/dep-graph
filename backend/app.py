# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_repo import init_db, get_all_nodes, update_node_status, initialize_graph, get_nodes_by_status

app = Flask(__name__)
CORS(app)

# Initialize DB on startup
init_db()

# Sample graph dependencies
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

@app.get("/api/graph")
def get_graph():
    # Fetch all current node statuses from the database
    rows = get_all_nodes()
    status_map = dict(rows)  # node_id -> status

    eligible_nodes = set()

    # Determine eligible nodes
    for node_id, deps in dependencies.items():
        if not deps:
            eligible_nodes.add(node_id)
        elif all(status_map.get(dep) != "pending" for dep in deps):
            eligible_nodes.add(node_id)

    # Build nodes with eligible flag
    nodes = []
    for node_id in dependencies.keys():
        nodes.append({
            "id": node_id,
            "status": status_map.get(node_id, "unknown"),
            "eligible": node_id in eligible_nodes
        })

    # Build dependency links
    links = [
        {"source": dep, "target": node_id}
        for node_id, deps in dependencies.items()
        for dep in deps
    ]

    # Final graph structure
    graph = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": nodes,
        "links": links
    }

    return jsonify(graph), 200


@app.post("/api/graph/node/<node_id>/status")
def update_node_status_api(node_id):
    data = request.get_json()
    update_node_status(node_id, data.get("status"))
    return jsonify({"message": "Node status updated successfully"}), 200

@app.get("/api/graph/next")
def get_next_node():
    rows = get_all_nodes()
    for node_id, status in rows:
        if status == "pending":
            return jsonify({"next_node": node_id}), 200
    return jsonify({"message": "No pending nodes found"}), 200

@app.post("/api/graph")
def create_graph():
    initialize_graph(dependencies)
    return jsonify({"message": "Graph initialized successfully"}), 200

@app.get("/api/graph/eligible")
def get_eligible_nodes():
    eligible_nodes = get_nodes_by_status("in-progress")
    return jsonify({"eligible_nodes": eligible_nodes}), 200

if __name__ == "__main__":
    app.run(debug=True)
