import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

const API_URL = 'http://localhost:5000/api/graph';

fetch(API_URL)
  .then(res => res.json())
  .then(data => {
    const enriched = enrichNodeStatus(data);
    renderGraph(enriched);
  })
  .catch(err => {
    console.error('Failed to load graph data:', err);
  });

function enrichNodeStatus(data) {
  const doneNodes = new Set(data.nodes.filter(n => n.status === 'done').map(n => n.id));
  const dependencies = new Map();

  for (const link of data.links) {
    if (!dependencies.has(link.target)) {
      dependencies.set(link.target, []);
    }
    dependencies.get(link.target).push(link.source);
  }

  const updatedNodes = data.nodes.map(node => {
    if (node.status === 'done') return node;
    const deps = dependencies.get(node.id) || [];
    if (deps.length === 0 || deps.every(dep => doneNodes.has(dep))) {
      return { ...node, status: 'in-progress' };
    }
    return { ...node, status: 'pending' };
  });

  return { ...data, nodes: updatedNodes };
}

function renderGraph(data) {
  const nodes = data.nodes.map(node => ({
    data: { id: node.id, status: node.status }
  }));

  const edges = data.links.map(link => ({
    data: { source: link.source, target: link.target }
  }));

  const cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [...nodes, ...edges],
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(id)',
          'text-valign': 'center',
          'color': '#fff',
          'text-outline-color': '#888',
          'text-outline-width': 2,
          'background-color': ele => {
            const status = ele.data('status');
            if (status === 'done') return '#4caf50';       // green
            if (status === 'in-progress') return '#ffeb3b'; // yellow
            return '#9e9e9e';                               // gray
          },
          'shape': 'roundrectangle',
          'width': 150,
          'height': 50,
          'font-size': '12px'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#ccc',
          'target-arrow-color': '#ccc',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier'
        }
      }
    ],
    layout: {
      name: 'dagre',
      rankDir: 'BT',  // Top to bottom (leaf to root)
      nodeSep: 50,
      edgeSep: 10,
      rankSep: 100
    }
  });

  // Adding a click event listener to nodes for status updates
  cy.on('tap', 'node', function(event) {
    const node = event.target;
    const currentStatus = node.data('status');
    const newStatus = currentStatus === 'done' ? 'pending' : 'done'; // toggle status for example
    node.data('status', newStatus);

    // Update the UI (change color, etc.)
    node.style({
      'background-color': newStatus === 'done' ? '#4caf50' : '#9e9e9e'
    });
console.log(node);
    // Optionally, call an API to save the updated status
    updateNodeStatusInAPI(node.id(), newStatus);
    console.log(typeof node.id); // Is it a function or string?
console.log(node.id);
  });
}

// Function to update node status in your backend API
function updateNodeStatusInAPI(nodeId, newStatus) {
  fetch(`http://localhost:5000/api/graph/node/${nodeId}/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status: newStatus }),
  })
  .then(res => res.json())
  .then(data => {
    console.log('Node status updated:', data);
  })
  .catch(err => {
    console.error('Error updating node status:', err);
  });
}
