// src/App.jsx
import React, { useEffect, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import axios from "axios";
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
cytoscape.use(dagre);


const App = () => {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchGraph = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/graph");
      const { nodes, links } = response.data;

      const cyNodes = nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.id,
          status: node.status,
          eligible: node.eligible
        }
      }));

      const cyEdges = links.map((link) => ({
        data: {
          source: link.source,
          target: link.target
        }
      }));

      setElements([...cyNodes, ...cyEdges]);
    } catch (error) {
      console.error("Failed to fetch graph data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const style = [
    {
      selector: "node",
      style: {
        "label": "data(label)",
        "background-color": (ele) =>
          ele.data("eligible") ? "#90ee90" : "#87CEFA", // green for eligible, blue otherwise
        "text-valign": "center",
        "text-halign": "center",
        "width": 50,
        "height": 50,
        "font-size": "10px"
      }
    },
    {
      selector: "edge",
      style: {
        "width": 2,
        "line-color": "#ccc",
        "target-arrow-color": "#ccc",
        "target-arrow-shape": "triangle"
      }
    }
  ];

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ width: "100%", height: "600px" }}>
      <CytoscapeComponent
        elements={elements}
        style={{ width: "100%", height: "100%" }}
        stylesheet={style}
        layout={{ name: "dagre" }} // You can change to "breadthfirst", "cose", etc.
      />
    </div>
  );
};

export default App;
