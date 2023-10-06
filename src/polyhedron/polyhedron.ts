import { Edge, Graph, LineGraph, Vertex } from "./graph";
import { ITreeNode, coverList } from "./tree";

export type Vector = [number, number, number];

export interface IPolyhedron {
  // new(coordinates: Map<Vertex, Vector>, vertexGraph: Graph): IPolyhedron;
  getPolarCoordinates(): Array<Vector>;
  getCartesianCoordinates(): Array<Vector>;
  getCartesianCover(): Array<Vector>;
}

class Polyhedron implements IPolyhedron {
  constructor(private polarCoordinates: Map<Vertex, Vector>, private vertexGraph: Graph) {}
  getPolarCoordinates(): Array<Vector> {
    return Array.from(this.polarCoordinates.values())
  }

  getCartesianCoordinates(): Array<Vector> {
    const arr: Array<Vector> = Array.from(this.polarCoordinates.values());
    arr.forEach(toCartesian);
    return arr
  }

  getCartesianCover(): Array<Vector> {
    const lineGraph = new LineGraph(this.vertexGraph);
    const coverTree = lineGraph.coverTree() as ITreeNode<Edge>;
    const edgeCoverList: Array<Vertex> = coverList(coverTree);
    let vertexCover = new Array<Vertex>();
    for (let i = 0; i < edgeCoverList.length - 1; i++) {
      const vertices: [Vertex, Vertex] = parseEdgePair(edgeCoverList[i], edgeCoverList[i + 1]);
      vertexCover = vertexCover.concat(vertices);
    }

    let vectors = new Array<Vector>;
    vertexCover.forEach((v: Vertex): void => {
      console.assert(this.polarCoordinates.has(v));
      const vector = toCartesian(this.polarCoordinates.get(v) as Vector);
      vectors = vectors.concat(vector);   
    });

    return vectors;
  }
}

export interface IPolyhedronFactory {
  getDodecahedron(r: number): IPolyhedron;
}

export class PolyhedronFactory implements IPolyhedronFactory {
  constructor() {}
  getDodecahedron(R: number): IPolyhedron {
    const RADIAN_DEGREE = Math.PI / 180;
    const ALPHA = Math.asin(Math.sqrt(3) / 3);
    const BETA = Math.acos(Math.sqrt(3) / (6 * Math.sin(54 * RADIAN_DEGREE)));

    const polarCoordinates = new Map<Vertex, Vector>([
      ["A", [R, (Math.PI / 4) + 0*(Math.PI / 2), ALPHA]],
      ["B", [R, (Math.PI / 4) + 1*(Math.PI / 2), ALPHA]],
      ["C", [R, (Math.PI / 4) + 2*(Math.PI / 2), ALPHA]],
      ["D", [R, (Math.PI / 4) + 3*(Math.PI / 2), ALPHA]],
      ["H", [R, (Math.PI / 4) + 0 * (Math.PI / 2), -ALPHA]],
      ["E", [R, (Math.PI / 4) + 1 * (Math.PI / 2), -ALPHA]],
      ["F", [R, (Math.PI / 4) + 2 * (Math.PI / 2), -ALPHA]],
      ["G", [R, (Math.PI / 4) + 3 * (Math.PI / 2), -ALPHA]],
      ["I", [R, BETA, 0]],
      ["J", [R, Math.PI - BETA, 0]],
      ["L", [R, Math.PI + BETA, 0]],
      ["M", [R, -BETA, 0]],
      ["S", [R, Math.PI / 2, BETA]],
      ["Q", [R, Math.PI / 2, Math.PI - BETA]],
      ["R", [R, Math.PI / 2, Math.PI + BETA]],
      ["T", [R, Math.PI / 2, -BETA]],
      ["N", [R, 2 * Math.PI, (Math.PI/ 2 - BETA)]],
      ["O", [R, 2 * Math.PI, -(Math.PI / 2 - BETA)]],
      ["K", [R, Math.PI, (Math.PI / 2 - BETA)]],
      ["P", [R, Math.PI, -(Math.PI / 2 - BETA)]],
    ]);

    const vertices: Array<Vertex> = [
        "A",
        "B",
        "C",
        "D",
        "H",
        "E",
        "F",
        "G",
        "I",
        "J",
        "L",
        "M",
        "S",
        "Q",
        "R",
        "T",
        "N",
        "O",
        "K",
        "P",
    ];

    const links = new Map<Vertex, [Vertex, Vertex, Vertex]>([
      ["A", ["N", "S", "I"]],
      ["B", ["K", "J", "S"]],
      ["C", ["K", "Q", "L"]],
      ["D", ["Q", "M", "N"]],
      ["H", ["O", "I", "T"]],
      ["E", ["J", "P", "T"]],
      ["F", ["P", "R", "L"]],
      ["G", ["R", "O", "M"]],
      ["I", ["J", "H", "A"]],
      ["J", ["I", "E", "B"]],
      ["L", ["F", "M", "C"]],
      ["M", ["L", "G", "D"]],
      ["S", ["Q", "A", "B"]],
      ["Q", ["C", "D", "S"]],
      ["R", ["G", "F", "T"]],
      ["T", ["H", "E", "R"]],
      ["N", ["A", "D", "O"]],
      ["O", ["H", "G", "N"]],
      ["K", ["B", "C", "P"]],
      ["P", ["E", "F", "K"]],
    ]);

    const graph = new Graph();
    vertices.forEach((v: Vertex): void => {
      graph.addVertex(v);
    });
    vertices.forEach((v: Vertex): void => {
      links.get(v)?.forEach((adj: Vertex): void => {
        console.log(v, adj);
        graph.addEdge(v, adj);
      });
    });
    return new Polyhedron(polarCoordinates, graph);
  }
}

export function toCartesian(vector: Vector): Vector {
  const r: number = vector[0];
  const teta: number = vector[1];
  const phi: number = vector[2];
  return [
    r * Math.cos(phi) * Math.cos(teta),
    r * Math.cos(phi) * Math.sin(teta),
    r * Math.sin(phi),
  ];
}

function parseEdgePair(lhs: Edge, rhs: Edge): [Vertex, Vertex] {
  const lVertices: Array<Vertex> = lhs.split("/");
  console.assert(lVertices.length == 2);
  const rVertices: Array<Vertex> = rhs.split("/");
  console.assert(rVertices.length == 2);
  let matchingIndexes: [number, number] = [-1, -1];
  for (let i = 0; i < lVertices.length; i++) {
    for (let j = 0; j < rVertices.length; j++) {
      if (lVertices[i] == rVertices[j]) {
        matchingIndexes = [i, j];
      }
    }
  }
  if (matchingIndexes[0] == -1) {
    throw new Error("Edges are not related");
  }
  if (matchingIndexes[0] == 0) {
    lVertices.reverse();
  }
  return [lVertices[0], lVertices[1]];
}

export const IPolyhedron = Polyhedron;