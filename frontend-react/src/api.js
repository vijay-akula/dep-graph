import axios from 'axios';

export const fetchGraphData = async () => {
  const res = await axios.get('/api/graph');
  return res.data;
};

// src/components/Graph.jsx
import React, { useEffect, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { fetchGraphData } from '../api';

const statusColors = {
  done: 'green',
  pending: 'orange',
  failed: 'red',
  unknown: 'gray',
};

export default function Graph() {
  const [elements, setElements] = useState([]);

  useEffect(() => {
    fetchGraphData().then((data) => {
      const nodes = data.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          status: node.status,
        },
      }));

      const edges = data.flatMap((node) =>
        node.dependencies.map((dep) => ({
          data: { source: node.id, target: dep },
        }))
      );

      setElements([...nodes, ...edges]);
    });
  }, []);

  return (
    <CytoscapeComponent
      elements={elements}
      style={{ width: '100%', height: '600px' }}
      layout={{ name: 'dagre' }}
      stylesheet={[
        {
          selector: 'node',
          style: {
            'background-color': (ele) => statusColors[ele.data('status')] || 'gray',
            label: 'data(label)',
            'text-valign': 'center',
            color: '#fff',
            'font-size': '12px',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#ccc',
            'target-arrow-color': '#ccc',
            'target-arrow-shape': 'triangle',
          },
        },
      ]}
    />
  );
}
