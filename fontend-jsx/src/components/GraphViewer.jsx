// GraphViewer.jsx
import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

const API_URL = 'http://localhost:5000/api/graph';

const thStyle = {
  textAlign: 'left',
  padding: '8px',
  backgroundColor: '#f0f0f0',
  borderBottom: '2px solid #999'
};

const tdStyle = {
  padding: '8px'
};

const GraphViewer = () => {
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [layoutDirection, setLayoutDirection] = useState('TB');
  const [versionActionView, setVersionActionView] = useState(null);
  const [promptInput, setPromptInput] = useState('');
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    fetch(API_URL)
      .then(res => res.json())
      .then(data => {
        const enriched = enrichNodeStatus(data);
        setGraphData(enriched);
        renderGraph(enriched);
      })
      .catch(err => {
        console.error('Failed to load graph data:', err);
      });
  }, [layoutDirection]);

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
      container: cyRef.current,
      elements: [...nodes, ...edges],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(id)',
            'text-valign': 'center',
            'color': '#fff',
            'text-outline-color': '#333',
            'text-outline-width': 2,
            'background-color': ele => {
              const status = ele.data('status');
              if (status === 'done') return '#4caf50';
              if (status === 'in-progress') return '#ffeb3b';
              return '#9e9e9e';
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
        rankDir: layoutDirection,
        nodeSep: 50,
        edgeSep: 10,
        rankSep: 100
      }
    });

    cy.on('tap', 'node', function (event) {
      const node = event.target;
      setSelectedNode(node.id());
      setVersionActionView(null);
    });
  }

  const handleVersionAction = (action, version) => {
    if (action === 'view') {
      setVersionActionView('view');
    }
  };

  const handleRefreshGraph = () => {
    if (graphData) {
      const enriched = enrichNodeStatus(graphData);
      setGraphData(enriched);
      renderGraph(enriched);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <label>Layout Direction: </label>
        <select value={layoutDirection} onChange={e => setLayoutDirection(e.target.value)}>
          <option value="TB">Top to Bottom</option>
          <option value="BT">Bottom to Top</option>
          <option value="LR">Left to Right</option>
        </select>
        <button onClick={handleRefreshGraph} style={{ marginLeft: '1rem' }}>Refresh Graph</button>
      </div>
      <div ref={cyRef} style={{ width: '100%', height: '500px', border: '1px solid #ccc' }}></div>

      {selectedNode && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Node: {selectedNode}</h3>

          <div style={{ marginTop: '1rem' }}>
            <h4>Versions</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
              <thead>
                <tr>
                  <th style={thStyle}>Version</th>
                  <th style={thStyle}>Created At</th>
                  <th style={thStyle}>Status</th>
                  <th style={thStyle}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {[{ version: 'v1.0', created: '2024-01-01', status: 'draft' }, { version: 'v1.1', created: '2024-02-15', status: 'review' }, { version: 'v2.0', created: '2024-03-10', status: 'approved' }].map((ver, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #ccc' }}>
                    <td style={tdStyle}>{ver.version}</td>
                    <td style={tdStyle}>{ver.created}</td>
                    <td style={tdStyle}>{ver.status}</td>
                    <td style={tdStyle}>
                      <button onClick={() => handleVersionAction('view', ver)}>View</button>
                      <button style={{ marginLeft: '8px' }}>Edit</button>
                      <button style={{ marginLeft: '8px' }}>Accept</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {versionActionView === 'view' && (
            <div style={{ marginTop: '1rem' }}>
              <h4>Version Details</h4>
              <input
                placeholder="Enter prompt"
                value={promptInput}
                onChange={e => setPromptInput(e.target.value)}
                style={{ width: '100%', padding: '8px', marginBottom: '0.5rem' }}
              />
              <div>
                <button>View Code</button>
                <button style={{ marginLeft: '8px' }}>Generate Tech Spec</button>
                <button style={{ marginLeft: '8px' }}>Generate Flow Chart</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GraphViewer;
