import { describe, expect, test, beforeEach } from '@jest/globals';
import { AbstractGraph, Graph, ITraversalCallback, LineGraph, Vertex } from "./graph";
import { ITreeNode } from './tree';

function getRootOnlyGraph(v: Vertex): Graph {
  const graph = new Graph();
  graph.addVertex(v);
  return graph;
}

function getMinimalLinkedGraph(lhs: Vertex, rhs: Vertex): Graph {
  const graph = new Graph();
  graph.addVertex(lhs);
  graph.addVertex(rhs);
  graph.addEdge(lhs, rhs);
  return graph;
}

function getSquareGraph(vertices: Array<Array<Vertex>>): Graph {
  const graph = new Graph();
  vertices.forEach((row) => {
    row.forEach((v) => {
      graph.addVertex(v);
    });
  });
  graph.addEdge(vertices[0][0], vertices[0][1]);
  graph.addEdge(vertices[0][0], vertices[1][0]);
  graph.addEdge(vertices[0][1], vertices[1][1]);
  graph.addEdge(vertices[1][0], vertices[1][1]);
  return graph;
}

describe("Graph", () => {
  let graph: Graph;
  describe("is null graph", () => {
    beforeEach(() => {
      graph = new Graph();
    });
    test("root is null", () => {
      expect(graph.getRoot()).toBeNull();
    });
    test("getEdge throws", () => {
      expect(() => graph.getEdge("B", "C")).toThrow();
    });
    test("dfs does nothing", () => {
      let it = 0;
      graph.dfs((vertex: Vertex): void => {it++});
      expect(it).toEqual(0);
    });
    test("coverTree is null", () => {
      expect(graph.coverTree()).toBeNull();
    });
  });

  describe("is root-only graph", () => {
    const expectedRoot: Vertex = "A";
    let root: Vertex | null;
    beforeEach(() => {
      graph = getRootOnlyGraph(expectedRoot)
      root = graph.getRoot();
    })
    test("root is not null", () => {
      expect(graph.getRoot()).toEqual(expectedRoot);
    });
    test("root has zero adjacent vertices", () => {
      expect(graph.getAdjacent(root as Vertex).length).toEqual(0);
    });
    test("dfs traverses only root", () => {
      let vertices = new Array<Vertex>();
      graph.dfs((vertex: Vertex): void => {vertices = vertices.concat(vertex)});
      expect(vertices.length).toEqual(1);
      expect(vertices[0]).toEqual(expectedRoot);
    });
    test("coverTree has one node", () => {
      const tree = graph.coverTree() as ITreeNode<Vertex>;
      expect(tree.children.length).toEqual(0);
      expect(tree.value).toEqual(expectedRoot);
    });
  });

  describe("has two linked vertices", () => {
    const expectedVertexA: Vertex = "A";
    const expectedVertexB: Vertex = "B";
    let root: Vertex | null;
    beforeEach(() => {
      graph = getMinimalLinkedGraph(expectedVertexA, expectedVertexB);
      root = graph.getRoot();
    });
    test("root is the first added vertex", () => {
      expect(root).toEqual(expectedVertexA);
    });
    test("root has single adjacent vertex equals second added vertex", () => {
      const adj: Array<Vertex> = graph.getAdjacent(root as Vertex);
      expect(adj.length).toEqual(1);
      expect(adj[0]).toEqual(expectedVertexB);
    });
    test("coverTree has two nodes", () => {
      const tree = graph.coverTree() as ITreeNode<Vertex>;
      expect(tree.children.length).toEqual(1);
      expect(tree.value).toEqual(expectedVertexA);
      expect(tree.children[0].value).toEqual(expectedVertexB);
    });
  });

  describe("is square graph", () => {
    let graph: Graph;
    const vertices = [
      ["A", "B"],
      ["C", "D"],
    ];
    beforeEach(() => {
      graph = getSquareGraph(vertices);
    });
    test("root and leaf has two links", () => {
      const rAdj: Array<Vertex> = graph.getAdjacent(vertices[0][0]);
      const lAdj: Array<Vertex> = graph.getAdjacent(vertices[1][1]);
      expect(rAdj.length).toEqual(2);
      expect(rAdj.includes(vertices[0][1]) && rAdj.includes(vertices[1][0])).toEqual(true);
      expect(lAdj.length).toEqual(2);
      expect(lAdj.includes(vertices[0][1]) && lAdj.includes(vertices[1][0])).toEqual(true);
    });
    test("coverTree has two nodes", () => {
      const tree = graph.coverTree() as ITreeNode<Vertex>;
      const expectedTree = {
        value: vertices[0][0],
        children: [
          {
            value: vertices[0][1],
            children: [
              {
                value: vertices[1][1],
                children: [
                  {
                    value: vertices[1][0],
                    children: [],
                  },
                ],
              },
            ],
          },
        ]
      }
      expect(tree).toEqual(expectedTree);
    });
  });
});

describe("Line graph", () => {
  let originalGraph: Graph;
  describe("original graph is null graph", () => {
    beforeEach(() => {
      originalGraph = new Graph();
    });
    test("line graph is null graph", () => {
      const lineGraph = new LineGraph(originalGraph);
      expect(lineGraph.getRoot()).toBeNull();
    });
  });
  describe("original graph is root-only graph", () => {
    const root: Vertex = "A";
    beforeEach(() => {
      originalGraph = getRootOnlyGraph(root);
    });
    test("line graph is null graph", () => {
      const lineGraph = new LineGraph(originalGraph);
      expect(lineGraph.getRoot()).toBeNull();
    });
  });
  describe("original graph is minimal linked graph", () => {
    const expectedVertexA: Vertex = "A";
    const expectedVertexB: Vertex = "B"; 
    beforeEach(() => {
      originalGraph = getMinimalLinkedGraph(expectedVertexA, expectedVertexB);
    });
    test("line graph has one node", () => {
      const lineGraph = new LineGraph(originalGraph);
      let it = 0;
      lineGraph.dfs((v: Vertex) => it++);
      expect(it).toEqual(1);
      const lineGraphRoot = lineGraph.getRoot() as Vertex;
      expect(lineGraphRoot).toEqual("A/B");
    });
  });
  describe("original graph is square", () => {
    const vertices = [
      ["A", "B"],
      ["C", "D"],
    ];
    beforeEach(() => {
      originalGraph = getSquareGraph(vertices);
    });
    test("contains correct vertices", () => {
      const lineGraph = new LineGraph(originalGraph);
      const expectedAdj = new Map<Vertex, Set<Vertex>>([
        ["A/B", new Set<Vertex>(["A/C", "B/D"])],
        ["A/C", new Set<Vertex>(["A/B", "C/D"])],
        ["B/D", new Set<Vertex>(["A/B", "C/D"])],
        ["C/D", new Set<Vertex>(["B/D", "A/C"])],
      ]);
      const matched = new Map<Vertex, boolean>([
        ["A/B", false],
        ["A/C", false],
        ["B/D", false],
        ["C/D", false],
      ]);
      lineGraph.dfs((v: Vertex): void => {
        expect(expectedAdj.has(v)).toEqual(true);
        const expectedVAdj = expectedAdj.get(v) as Set<Vertex>;
        const adj = new Set<Vertex>(lineGraph.getAdjacent(v));
        let match = true;
        adj.forEach((v: Vertex): void => {
          match &&= expectedVAdj.has(v);
        });
        expectedVAdj.forEach((v: Vertex): void => {
          match &&= adj.has(v);
        });
        expect(match).toEqual(true);
      });
    });
  });
});
