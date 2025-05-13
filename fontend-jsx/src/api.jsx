import axios from 'axios';

const API_URL = 'http://localhost:5000/api/graph/node';

export const updateNodeStatus = async (nodeId, status) => {
  try {
    const response = await axios.post(`${API_URL}/${nodeId}/status`, { status });
    return response.data;
  } catch (error) {
    console.error("Error updating node status", error);
    throw error;
  }
};
