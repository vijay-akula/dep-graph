from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import DependencyRequest, NodeUpdateRequest
from graph_utils import build_graph, get_next_file_to_convert, update_node_status, get_status_map, init_db
import networkx as nx
import asyncio

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

G = nx.DiGraph()

@app.on_event("startup")
async def startup():
    await init_db()

@app.post("/api/graph")
async def upload_graph(deps: DependencyRequest):
    global G
    G = build_graph(deps.file_dependencies)
    return {"message": "Graph updated."}

@app.get("/api/graph")
async def get_graph():
    global G
    status_map = await get_status_map()
    graph_data = nx.node_link_data(G)
    for node in graph_data['nodes']:
        node.setdefault("id", node.get("name"))
        node["status"] = status_map.get(node['id'], "default")
    return graph_data

@app.get("/api/graph/next")
async def next_file():
    global G
    next_files = await get_next_file_to_convert(G)
    return {"next_files": next_files}

@app.post("/api/graph/node/{node_id}/status")
async def update_status(node_id: str, req: NodeUpdateRequest):
    await update_node_status(node_id, req.status)
    return {"message": f"Status for {node_id} updated to {req.status}"}