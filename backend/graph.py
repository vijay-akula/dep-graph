dependencies = {}
all_nodes = set()

def init_graph(dep_map):
    global dependencies, all_nodes
    dependencies = dep_map
    all_nodes = set(dep_map.keys())
    for v in dep_map.values():
        all_nodes.update(v)

def get_graph_with_statuses(statuses):
    nodes = [{'id': node, 'status': statuses.get(node, 'pending')} for node in sorted(all_nodes)]
    links = []
    for tgt, srcs in dependencies.items():
        for src in srcs:
            links.append({'source': src, 'target': tgt})
    return {
        'directed': True,
        'multigraph': False,
        'graph': {},
        'nodes': nodes,
        'links': links
    }

def get_next_nodes(statuses):
    ready_nodes = []
    for node in all_nodes:
        if statuses.get(node, 'pending') != 'pending':
            continue
        deps = [dep for dep in dependencies.get(node, [])]
        if all(statuses.get(dep, 'pending') == 'done' for dep in deps):
            ready_nodes.append(node)
    return sorted(ready_nodes)
