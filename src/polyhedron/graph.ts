import { addEmitHelper } from "typescript";

type Vertex = string;
type Edge = string;

interface IGraph {
  addVertex(vertex: Vertex): void;
  getEdge(lhs: Vertex, rhs: Vertex): Edge;
  addEdge(lhs: Vertex, rhs: Vertex): Edge;
  addEdges(lhs: Vertex, ...more: Vertex[]): Edge[];
  getAdjacent(vertex: Vertex): Vertex[];
  dfs(callback: ITraversalCallback): void;
}

interface ITraversalCallback {
  (node: Vertex): void;
}

export function createGraph(): IGraph {
  const adj = new Map<Vertex, Vertex[]>();
  let root: null | Vertex = null;

  function addVertex(vertex: Vertex): void {
    if (adj.has(vertex)) {
      throw new Error("Vertex already exists");
    }
    if (vertex.includes('/')) {
      throw new Error("Vertex name could not include \'/\'")
    }
    if (root == null) {
      root = vertex;
    }
    adj.set(vertex, new Array<Vertex>());
  }

  function getEdge(lhs: Vertex, rhs: Vertex): Edge {
    if (!adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }
    return getEdge(lhs, rhs);
  }

  function addEdge(lhs: Vertex, rhs: Vertex): Edge {
    if (!adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }

    const lAdj = adj.get(lhs) as Vertex[];
    if (lAdj.includes(rhs)) {
      return getEdge(lhs, rhs);
    }
    adj.set(lhs, lAdj.concat(rhs));
    const rAdj = adj.get(rhs) as Vertex[];
    adj.set(rhs, rAdj.concat(lhs));
    return getEdge(lhs, rhs);
  };

  function addEdges(lhs: Vertex, ...more: Vertex[]): Edge[] {
    let edges = new Array<Edge>();
    more.forEach((rhs) => {
      const edge = addEdge(lhs, rhs);
      edges = edges.concat(edge);
    });
    return edges;
  };

  function getAdjacent(vertex: Vertex): Vertex[] {
    const v = adj.get(vertex);
    return v == undefined ? new Array() : v;
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
    getEdge,
    addEdge,
    addEdges,
    getAdjacent,
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

function lineGraphGetVertices(vertex: Vertex): Array<Vertex> {
  const vertices: Array<Vertex> = vertex.split('-');
  if (vertices.length != 2) {
    throw new Error("Vertex is not line graph's vertex");
  }
  return vertices;
}

function toLineGraph(
  graph: IGraph,
  ): IGraph {
  const lineGraph = createGraph();
  const edges = new Set<Edge>();
  graph.dfs((vertex: Vertex): void => {
    graph.getAdjacent(vertex).forEach((adjVertex: Vertex): void => {
      edges.add(getEdge(vertex, adjVertex));
    })
  });
  let edgesArr = new Array<Edge>();
  edges.forEach((edge: Edge): void => {
    edgesArr = edgesArr.concat(edge);
    lineGraph.addVertex(edge.replace('/', '-'));
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
