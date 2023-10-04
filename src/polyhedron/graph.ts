import { addEmitHelper } from "typescript";

export type Vertex = string;
export type Edge = string;

export abstract class AbstractGraph {
  protected readonly adj: Map<Vertex, Vertex[]>;
  protected root: Vertex | null;

  constructor() {
    this.adj = new Map<Vertex, Vertex[]>();
    this.root = null;
  }

  protected abstract buildEdge(lhs: Vertex, rhs: Vertex): Edge;

  protected auxAddVertex(vertex: Vertex): void {
    if (this.root == null) {
      this.root = vertex;
    }
    this.adj.set(vertex, new Array<Vertex>());
  }

  protected auxAddEdge(lhs: Vertex, rhs: Vertex): Edge {
    const lAdj = this.adj.get(lhs) as Vertex[];
    if (lAdj.includes(rhs)) {
      return this.buildEdge(lhs, rhs);
    }
    this.adj.set(lhs, lAdj.concat(rhs));
    const rAdj = this.adj.get(rhs) as Vertex[];
    this.adj.set(rhs, rAdj.concat(lhs));
    return this.buildEdge(lhs, rhs);
  }

  getRoot(): Vertex | null {
    return this.root;
  }

  getAdjacent(vertex: Vertex): Vertex[] {
    const v = this.adj.get(vertex);
    return v == undefined ? new Array() : v;
  }

  getEdge(lhs: Vertex, rhs: Vertex): Edge {
    if (!this.adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!this.adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }
    return this.buildEdge(lhs, rhs);
  }

  dfs(callback: ITraversalCallback): void {
    if (this.root == null) {
      return;
    }
    const visited = new Map<Vertex, boolean>();
    const adj: Map<Vertex, Vertex[]> = this.adj;
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
    recursiveDfs(this.root, callback);
  };
}

export class Graph extends AbstractGraph {
  protected buildEdge(lhs: Vertex, rhs: Vertex): Edge {
    return lhs < rhs ? lhs + '/' + rhs : rhs + '/' + lhs;
  }

  addVertex(vertex: Vertex): void {
    if (this.adj.has(vertex)) {
      throw new Error("Vertex already exists");
    }
    if (vertex.includes('/')) {
      throw new Error("Vertex name could not include \'/\'")
    }
    this.auxAddVertex(vertex);
  }

  addEdge(lhs: Vertex, rhs: Vertex): Edge {
    if (!this.adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!this.adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }
    return this.auxAddEdge(lhs, rhs);
  };

  addEdges(lhs: Vertex, ...more: Vertex[]): Edge[] {
    let edges = new Array<Edge>();
    more.forEach((rhs) => {
      const edge = this.addEdge(lhs, rhs);
      edges = edges.concat(edge);
    });
    return edges;
  };
}

export class LineGraph extends AbstractGraph {
  constructor(graph: Graph) {
    super();
    const edges = new Set<Edge>();
    graph.dfs((vertex: Vertex): void => {
      graph.getAdjacent(vertex).forEach((adjVertex: Vertex): void => {
        edges.add(graph.getEdge(vertex, adjVertex));
      })
    });
    let edgesArr = new Array<Edge>();
    edges.forEach((edge: Edge): void => {
      edgesArr = edgesArr.concat(edge);
      this.addVertex(edge);
    })
    
    for (let i = 0; i < edgesArr.length - 1; i++) {
      const edge: Edge = edgesArr[i];
      for (let j = i; j < edgesArr.length; j++) {
        const otherEdge: Edge = edgesArr[j];
        if (this.isPlainEdgesRelated(edge, otherEdge)) {
          this.addEdge(edge, otherEdge);
        }
      }
    }
  }

  private getPlainVertices(edge: Edge): Vertex[] {
    const vertices = edge.split('/');
    if (vertices.length != 2) {
      throw new Error("Vertices count does not equal 2");
    }
    return vertices;
  } 
  
  private isPlainEdgesRelated(lhs: Edge, rhs: Edge): boolean {
    const set = new Set<Vertex>();
    let related = false;
    const lVertices: Vertex[] = this.getPlainVertices(lhs);
    const rVertices: Vertex[] = this.getPlainVertices(rhs);
    const vertices = lVertices.concat(rVertices);
    vertices.forEach((vertex: Vertex): void => {
      if (set.has(vertex)) {
        related = true;
        return;
      }
    });
    return related;
  }

  protected buildEdge(lhs: Vertex, rhs:Vertex): Edge {
    const lVertices: Array<Edge> = lhs.split("/");
    const rVertices: Array<Edge> = rhs.split("/");
    if ((lVertices[0] = rVertices[0]) || (lVertices[0] = rVertices[1])) {
      return lVertices[0];
    } else if ((lVertices[1] = rVertices[0]) || (lVertices[1] = rVertices[1])) {
      return lVertices[1];
    }
    throw new Error("Vertices are not related"); 
  }

  private addVertex(vertex: Vertex): void {
    if (this.adj.has(vertex)) {
      throw new Error("Vertex already exists");
    }
    if (!vertex.includes('/')) {
      throw new Error("Vertex name must include \'/\'")
    }
    this.auxAddVertex(vertex);
  }

  private addEdge(lhs: Vertex, rhs: Vertex): Edge {
    if (!this.adj.has(lhs)) {
      throw new Error("lhs does not exist");
    }
    if (!this.adj.has(rhs)) {
      throw new Error("rhs does not exist");
    }
    return this.auxAddEdge(lhs, rhs);
  }
}

export interface ITraversalCallback {
  (node: Vertex): void;
}
