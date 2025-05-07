import cytoscape from 'cytoscape';

export function createGraph(elements) {
  return cytoscape({
    container: document.getElementById('graph-container'),
    elements: elements,
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#66ccff',
          'label': 'data(id)',
          'width': 50,
          'height': 50,
        },
      },
      {
        selector: 'edge',
        style: {
          'width': 3,
          'line-color': '#ccc',
          'target-arrow-color': '#ccc',
          'target-arrow-shape': 'triangle',
        },
      },
    ],
    layout: {
      name: 'grid',
      rows: 1,
    },
  });
}

export function addNode(cy, nodeData) {
  cy.add({ data: nodeData });
}

export function addEdge(cy, edgeData) {
  cy.add({ data: edgeData });
}
