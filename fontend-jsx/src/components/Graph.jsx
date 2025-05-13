import React, { useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { updateNodeStatus } from '../api';
import NodeStatusDialog from './NodeStatusDialog';

const Graph = () => {
  const [elements] = useState([
    { data: { id: 'a', label: 'Node A', status: 'active' } },
    { data: { id: 'b', label: 'Node B', status: 'inactive' } },
    { data: { id: 'c', label: 'Node C', status: 'active' } },
    { data: { source: 'a', target: 'b' } },
    { data: { source: 'b', target: 'c' } },
  ]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  const handleNodeClick = (event) => {
    const nodeId = event.target.id();
    setSelectedNode(nodeId);
    setOpenDialog(true);
  };

  const handleStatusChange = async (status) => {
    if (selectedNode) {
      await updateNodeStatus(selectedNode, status);
      setOpenDialog(false);
    }
  };

  const layout = {
    name: 'grid',
    rows: 1,
  };

  const styles = {
    node: {
      width: 100,
      height: 100,
      label: 'data(label)',
      backgroundColor: '#007bff',
      color: '#fff',
      textValign: 'center',
      textHalign: 'center',
    },
    edge: {
      width: 2,
      lineColor: '#ccc',
      targetArrowColor: '#ccc',
      targetArrowShape: 'triangle',
    },
  };

  return (
    <div>
      <CytoscapeComponent
        elements={elements}
        style={{ width: '100%', height: '500px' }}
        layout={layout}
        stylesheet={styles}
        cy={(cy) => cy.on('tap', 'node', handleNodeClick)}
      />
      {openDialog && (
        <NodeStatusDialog
          nodeId={selectedNode}
          onClose={() => setOpenDialog(false)}
          onStatusChange={handleStatusChange}
        />
      )}
    </div>
  );
};

export default Graph;
