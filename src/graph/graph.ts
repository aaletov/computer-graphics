import { addEmitHelper } from "typescript";

type Vertex = string;
type Edge = string;

interface IGraph<NodeLabel, EdgeLabel> {
  addVertex(vertex: Vertex): void;
  addEdge(lhs: Vertex, rhs: Vertex): void;
  addEdges(lhs: Vertex, ...more: Vertex[]): void;
  getAdjacent(vertex: Vertex): Vertex[];
  getLabel(vertex: Vertex): NodeLabel | undefined;
  setLabel(vertex: Vertex, label: NodeLabel): void;
  setEdgeLabel(lhs: Vertex, rhs: Vertex, label: EdgeLabel): void;
  getEdgeLabel(lhs: Vertex, rhs: Vertex): EdgeLabel | undefined;
  dfs(callback: ITraversalCallback): void;
}

interface ITraversalCallback {
  (node: Vertex): void;
}

export function createGraph<NodeLabel, EdgeLabel>(): IGraph<NodeLabel, EdgeLabel> {
  const labels = new Map<Vertex, NodeLabel>();
  const edgeLabels = new Map<Edge, EdgeLabel>();
  const adj = new Map<Vertex, Vertex[]>();
  let root: null | Vertex = null;

  function addVertex(vertex: Vertex): void {
    if (adj.has(vertex)) {
      throw new Error("Vertex already exists");
    }
    if (root == null) {
      root = vertex;
    }
    adj.set(vertex, new Array<Vertex>());
  }

  function addEdge(lhs: Vertex, rhs: Vertex): void {
    if (!adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }

    const lAdj = adj.get(lhs) as Vertex[];
    adj.set(lhs, lAdj.concat(rhs));
    const rAdj = adj.get(rhs) as Vertex[];
    adj.set(rhs, rAdj.concat(lhs));
  };

  function addEdges(lhs: Vertex, ...more: Vertex[]) {
    more.forEach((rhs) => {
      const edge = addEdge(lhs, rhs);
    });
  };

  function getAdjacent(vertex: Vertex): Vertex[] {
    const v = adj.get(vertex);
    return v == undefined ? new Array() : v;
  }

  function getLabel(vertex: Vertex): NodeLabel | undefined {
    return labels.get(vertex);
  }

  function setLabel(vertex: Vertex, label: NodeLabel): void {
    if (!adj.has(vertex)) {
      throw new Error("Vertex does not exist");
    }
    labels.set(vertex, label)
  }

  function getEdgeLabel(lhs: Vertex, rhs: Vertex): EdgeLabel | undefined {
    return edgeLabels.get(getEdge(lhs, rhs));
  }

  function setEdgeLabel(lhs: Vertex, rhs: Vertex, label: EdgeLabel): void {
    if (!adj.has(lhs)) {
      throw new Error("lhs does not exist")
    }
    if (!adj.has(rhs)) {
      throw new Error("rhs does not exist")
    }
    edgeLabels.set(getEdge(lhs, rhs), label);
  }  

  function dfs(callback: ITraversalCallback): void {
    if (root == null) {
      throw new Error("Graph is empty");
    }
    const visited = new Map<Vertex, boolean>();
    function recursiveDfs(root: Vertex, callback: ITraversalCallback): void {
      if (!adj.has(root)) {
        throw new Error("Vertex does not exist");
      }
      callback(root);
      visited.set(root, true);
      const rootChildren = adj.get(root) as Vertex[]; 
      rootChildren.forEach((child: Vertex): void => {
        if (visited.has(child)) {
          return;
        }
        recursiveDfs(child, callback);
      });
    }
    recursiveDfs(root, callback);
  };

  return {
    addVertex,
    addEdge,
    addEdges,
    getAdjacent,
    getLabel,
    setLabel,
    getEdgeLabel,
    setEdgeLabel,
    dfs,
  };
}

function getEdge(lhs: Vertex, rhs: Vertex): Edge {
  return lhs < rhs ? lhs + '/' + rhs : rhs + '/' + lhs;
}

function getVertices(edge: Edge): Vertex[] {
  const vertices = edge.split('/');
  if (vertices.length != 2) {
    throw new Error("Vertices count does not equal 2");
  }
  return vertices;
} 

function isEdgesRelated(lhs: Edge, rhs: Edge): boolean {
  const set = new Set<Vertex>();
  let related = false;
  getVertices(lhs).concat(getVertices(rhs)).forEach((vertex: Vertex): void => {
    if (set.has(vertex)) {
      related = true;
      return;
    }
  });
  return related;
}

interface IEdgeConverter<NodeLabel, EdgeLabel> {
  (lhs: NodeLabel, rhs: NodeLabel): EdgeLabel;
}

function setEdgeLabels<NodeLabel, EdgeLabel>(
  graph: IGraph<NodeLabel, EdgeLabel>,
  converter: IEdgeConverter<NodeLabel, EdgeLabel>,
): void {
  const visited = new Map<Vertex, boolean>();
  graph.dfs((vertex: Vertex): void => {
    graph.getAdjacent(vertex).forEach((adjVertex: Vertex): void => {
      if (visited.get(adjVertex) == true) {
        return;
      }
      const label: NodeLabel | undefined = graph.getLabel(vertex);
      const adjLabel: NodeLabel | undefined = graph.getLabel(adjVertex);
      if (!((label == undefined) || (adjLabel == undefined))) {
        const edgeLabel: EdgeLabel = converter(label, adjLabel);
        graph.setEdgeLabel(vertex, adjVertex, edgeLabel);
      }
    });
    visited.set(vertex, true);
  });
}

function toLineGraph<NodeLabel, EdgeLabel>(
  graph: IGraph<NodeLabel, EdgeLabel>,
  ): IGraph<EdgeLabel, NodeLabel> {
  const lineGraph = createGraph<EdgeLabel, NodeLabel>();
  const edges = new Set<Edge>();
  graph.dfs((vertex: Vertex): void => {
    graph.getAdjacent(vertex).forEach((adjVertex: Vertex): void => {
      edges.add(getEdge(vertex, adjVertex));
    })
  });
  let edgesArr = new Array<Edge>();
  edges.forEach((edge: Edge): void => {
    edgesArr = edgesArr.concat(edge);
    lineGraph.addVertex(edge);
  })
  
  for (let i = 0; i < edgesArr.length - 1; i++) {
    const edge: Edge = edgesArr[i];
    for (let j = i; j < edgesArr.length; j++) {
      const otherEdge: Edge = edgesArr[j];
      if (isEdgesRelated(edge, otherEdge)) {
        lineGraph.addEdge(edge, otherEdge);
      }
    }
  }

  return lineGraph;
}
