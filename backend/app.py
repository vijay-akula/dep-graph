from flask import Flask, request, jsonify
from db_repo import (
    init_db,
    get_all_nodes,
    update_node_status,
    get_nodes_by_status,
    insert_node,
    insert_dependency,
    get_dependencies_for_node,
)
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes or specify resources to allow specific origins
CORS(app, resources={r"/api/*": {"origins": "http://localhost:1234"}})


# Your existing API routes go here




@app.before_first_request
def setup():
    init_db()


def build_dependency_map():
    rows = get_all_nodes()
    graph = {node_id: {"status": status, "deps": []} for node_id, status in rows}

    for node_id in graph:
        deps = get_dependencies_for_node(node_id)
        graph[node_id]["deps"] = deps

    return graph


def get_eligible_nodes(graph):
    eligible = []
    for node_id, data in graph.items():
        if data["status"] == "done":
            continue
        deps = data["deps"]
        if not deps:
            eligible.append(node_id)
        else:
            if all(graph.get(dep, {}).get("status") != "pending" for dep in deps):
                eligible.append(node_id)
    return eligible


@app.post("/api/graph/init")
def initialize_graph():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload format"}), 400

    for node_id, deps in data.items():
        insert_node(node_id, "pending")
        for dep in deps:
            insert_node(dep, "pending")
            insert_dependency(node_id, dep)

    return jsonify({"message": "Graph initialized successfully"}), 201


@app.get("/api/graph")
def get_graph():
    graph = build_dependency_map()
    eligible_nodes = get_eligible_nodes(graph)

    nodes = [
        {
            "id": node_id,
            "status": data["status"],
            "eligible": node_id in eligible_nodes,
        }
        for node_id, data in graph.items()
    ]

    links = [
        {"source": dep, "target": node_id}
        for node_id, data in graph.items()
        for dep in data["deps"]
    ]

    return jsonify({
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": nodes,
        "links": links,
    }), 200


@app.get("/api/graph/eligible")
def get_eligible():
    graph = build_dependency_map()
    eligible = get_eligible_nodes(graph)
    return jsonify({"eligible_nodes": eligible}), 200


@app.post("/api/graph/update")
def update_status():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid payload format"}), 400

    for node_id, status in data.items():
        update_node_status(node_id, status)

    return jsonify({"message": "Status updated successfully"}), 200


@app.route("/api/graph/node/<node_id>/status", methods=["POST"])
def update_node_status_api(node_id):
    data = request.json  # Get JSON data sent with the POST request
    if not data or 'status' not in data:
        return jsonify({"error": "Status not provided"}), 400

    status = data['status']

    # Your logic to update node status in the database or any other action
    # For this example, we just print it (in production, you would update your database)
    update_node_status(node_id, status)
    print(f"Updating status of node {node_id} to {status}")

    # Send a success response
    return jsonify({"message": f"Node {node_id} status updated to {status}"}), 200



if __name__ == "__main__":
    app.run(debug=True)
