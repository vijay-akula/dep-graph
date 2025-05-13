import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

const GraphViewer = () => {
  const cyRef = useRef(null);
  const [layoutDir, setLayoutDir] = useState('TB');
  const [statusCounts, setStatusCounts] = useState({ done: 0, 'in-progress': 0, pending: 0 });
  const [selectedNode, setSelectedNode] = useState(null);
  const [viewMode, setViewMode] = useState(null); // "view" or "edit"

  useEffect(() => {
    loadGraph();
  }, [layoutDir]);

  const loadGraph = () => {
    fetch('http://localhost:5000/api/graph')
      .then(res => res.json())
      .then(data => {
        const enriched = enrichNodeStatuses(data);
        updateStatusCounts(enriched.nodes);
        renderGraph(enriched);
      })
      .catch(err => console.error('Failed to load graph:', err));
  };

  const updateStatusCounts = (nodes) => {
    const counts = { done: 0, 'in-progress': 0, pending: 0 };
    nodes.forEach(n => {
      counts[n.status] += 1;
    });
    setStatusCounts(counts);
  };

  const enrichNodeStatuses = (data) => {
    const doneNodes = new Set(data.nodes.filter(n => n.status === 'done').map(n => n.id));
    const dependencies = new Map();

    for (const link of data.links) {
      if (!dependencies.has(link.target)) dependencies.set(link.target, []);
      dependencies.get(link.target).push(link.source);
    }

    const updatedNodes = data.nodes.map(node => {
      if (node.status === 'done') return node;
      const deps = dependencies.get(node.id) || [];
      const allDepsDone = deps.every(dep => doneNodes.has(dep));

      if (deps.length === 0 || allDepsDone) {
        return { ...node, status: node.eligible ? 'in-progress' : 'pending' };
      } else {
        return { ...node, status: 'pending' };
      }
    });

    return { ...data, nodes: updatedNodes };
  };

  const renderGraph = (data) => {
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const elements = [
      ...data.nodes.map(n => ({
        data: { id: n.id, label: n.id, status: n.status, eligible: n.eligible }
      })),
      ...data.links.map(l => ({
        data: { source: l.source, target: l.target }
      }))
    ];

    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements,
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'color': ele => ele.data('status') === 'in-progress' ? '#000' : '#fff',
            'background-color': ele => {
              const s = ele.data('status');
              if (s === 'done') return '#4caf50';
              if (s === 'in-progress') return '#ffeb3b';
              return '#9e9e9e';
            },
            'text-outline-color': '#222',
            'text-outline-width': 1,
            'width': 140,
            'height': 50,
            'shape': 'roundrectangle',
            'font-size': '14px',
            'font-weight': 'bold',
            'cursor': 'pointer'
          }
        },
        {
          selector: 'edge',
          style: {
            width: 3,
            'line-color': '#999',
            'target-arrow-color': '#999',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: layoutDir,
        nodeSep: 70,
        edgeSep: 20,
        rankSep: 100
      }
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const status = node.data('status');
      const eligible = node.data('eligible');

      if (status === 'in-progress' && eligible) {
        node.data('status', 'done');
        node.style('background-color', '#4caf50');
        node.style('color', '#fff');

        fetch(`http://localhost:5000/api/graph/node/${node.data('id')}/status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'done' })
        })
          .then(res => res.json())
          .then(() => loadGraph())
          .catch(err => console.error('Failed to update status:', err));
      }

      setSelectedNode(node.data());
      setViewMode(null); // reset previous selection
    });

    cyRef.current = cy;
  };

  return (
    <div>
      <h2>Task Graph Viewer</h2>

      {/* Layout Selector */}
      <div style={{ marginBottom: '1rem' }}>
        <label>
          Layout Direction:&nbsp;
          <select value={layoutDir} onChange={e => setLayoutDir(e.target.value)}>
            <option value="TB">Top to Bottom</option>
            <option value="BT">Bottom to Top</option>
            <option value="LR">Left to Right</option>
          </select>
        </label>
      </div>

      {/* Status Counts */}
      <div style={{ marginBottom: '1rem' }}>
        <strong>Status Counts:</strong> ✅ Done: {statusCounts.done} | ⚠️ In Progress: {statusCounts['in-progress']} | ⏳ Pending: {statusCounts.pending}
      </div>

      {/* Graph Area */}
      <div id="cy" style={{ width: '100%', height: '600px', border: '1px solid #ccc', borderRadius: '8px' }} />

      {/* View/Edit Panel */}
      {selectedNode && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '6px', backgroundColor: '#f9f9f9' }}>
          <h3>Node: {selectedNode.id}</h3>
          <button onClick={() => setViewMode('view')} style={{ marginRight: '10px' }}>View</button>
          <button onClick={() => setViewMode('edit')}>Edit</button>

          {viewMode === 'view' && (
            <div style={{ marginTop: '1rem' }}>
              <h4>Viewing Details</h4>
              <p>Status: {selectedNode.status}</p>
              <p>Eligible: {selectedNode.eligible ? 'Yes' : 'No'}</p>
            </div>
          )}

          {viewMode === 'edit' && (
            <div style={{ marginTop: '1rem' }}>
              <h4>Edit Node (mock form)</h4>
              <label>
                Status:
                <select defaultValue={selectedNode.status}>
                  <option value="done">Done</option>
                  <option value="in-progress">In Progress</option>
                  <option value="pending">Pending</option>
                </select>
              </label>
              <br />
              <label>
                Eligible:
                <input type="checkbox" defaultChecked={selectedNode.eligible} />
              </label>
              <br />
              <button style={{ marginTop: '1rem' }}>Save (Not wired yet)</button>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div style={{ marginTop: '2rem' }}>
        <strong>Legend:</strong>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
          <LegendItem color="#4caf50" label="Done ✅" />
          <LegendItem color="#ffeb3b" label="In Progress ⚠️" />
          <LegendItem color="#9e9e9e" label="Pending ⏳" />
        </div>
      </div>
    </div>
  );
};

const LegendItem = ({ color, label }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
    <div style={{ width: 20, height: 20, backgroundColor: color, border: '1px solid #333' }}></div>
    <span>{label}</span>
  </div>
);

export default GraphViewer;
