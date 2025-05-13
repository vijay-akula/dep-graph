import React, { useState } from 'react';

const NodeStatusDialog = ({ nodeId, onClose, onStatusChange }) => {
  const [status, setStatus] = useState('active');

  const handleSubmit = () => {
    onStatusChange(status);
  };

  return (
    <div className="dialog">
      <div className="dialog-content">
        <h3>Update Node Status</h3>
        <p>Node ID: {nodeId}</p>
        <label>Status:</label>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="pending">Pending</option>
        </select>
        <button onClick={handleSubmit}>Submit</button>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default NodeStatusDialog;
