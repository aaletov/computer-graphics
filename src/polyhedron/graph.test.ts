import { describe, expect, test, beforeEach } from '@jest/globals';
import { AbstractGraph, Graph, ITraversalCallback, LineGraph, Vertex } from "./graph";

describe("null graph", () => {
  let graph: Graph;
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
  test("line graph is null graph", () => {
    const lineGraph = new LineGraph(graph);
    expect(lineGraph.getRoot()).toBeNull();
  });
});

describe("root-only graph", () => {
  let graph: Graph;
  let root: Vertex | null;
  const expectedRoot: Vertex = "A";
  beforeEach(() => {
    graph = new Graph();
    graph.addVertex("A");
    root = graph.getRoot();
  });
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
  test("line graph is null graph", () => {
    const lineGraph = new LineGraph(graph);
    expect(lineGraph.getRoot()).toBeNull();
  });
});

describe("graph with two vertices", () => {
  let graph: Graph;
  let root: Vertex | null;
  const expectedVertexA: Vertex = "A";
  const expectedVertexB: Vertex = "B";
  beforeEach(() => {
    graph = new Graph();
    graph.addVertex(expectedVertexA);
    graph.addVertex(expectedVertexB);
    graph.addEdge(expectedVertexA, expectedVertexB);
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
  test("line graph has one node", () => {
    const lineGraph = new LineGraph(graph);
    let it = 0;
    lineGraph.dfs((v: Vertex) => it++);
    expect(it).toEqual(1);
    const lineGraphRoot = lineGraph.getRoot() as Vertex;
    expect(lineGraphRoot).toEqual("A/B");
  });
});
