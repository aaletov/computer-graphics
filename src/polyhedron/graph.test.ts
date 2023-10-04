import { describe, expect, test, beforeEach } from '@jest/globals';
import { AbstractGraph, Graph, ITraversalCallback, LineGraph, Vertex } from "./graph";

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
});
