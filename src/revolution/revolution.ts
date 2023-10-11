import { mat3, vec3 } from "gl-matrix";
import { IPolyhedron, Vector } from "../polyhedron/polyhedron";

export enum Axis {
  X,
  Y,
  Z,
};

interface IRotationMatrixGetter {
  (angle: number): mat3;
};

function getRotationMatrixX(angle: number): mat3 {
  return new Float32Array([
    1, 0, 0,
    0, Math.cos(angle), -Math.sin(angle),
    0, Math.sin(angle), Math.cos(angle),
  ]);
}

function getRotationMatrixY(angle: number): mat3 {
  return new Float32Array([
    Math.cos(angle), 0, Math.sin(angle),
    0, 1, 0,
    -Math.sin(angle), 0, Math.cos(angle),
  ]);
}

function getRotationMatrixZ(angle: number): mat3 {
  return new Float32Array([
    Math.cos(angle), -Math.sin(angle), 0,
    Math.sin(angle), Math.cos(angle), 0,
    0, 0, 1,
  ]);
}

export function rotateVertex(vertex: vec3, angle: number, axis: Axis): vec3 {
  const axisMatrices = new Map<Axis, IRotationMatrixGetter>([
    [Axis.X, getRotationMatrixX],
    [Axis.Y, getRotationMatrixY],
    [Axis.Z, getRotationMatrixZ],
  ]);
  const rotationMatrixGetter = axisMatrices.get(axis) as IRotationMatrixGetter;
  const rotationMatrix = rotationMatrixGetter(angle);
  const oVertex = vec3.create();
  vec3.transformMat3(oVertex, vertex, rotationMatrix);
  return oVertex;
}

export function rotateLine(line: Array<vec3>, angle: number, axis: Axis): Array<vec3> {
  const oLine = new Array<vec3>();
  line.forEach((vertex: vec3): void => {
    oLine.push(rotateVertex(vertex, angle, axis));
  });
  return oLine;
}

export interface IRevolutionSolid {
  readonly coordinates: Array<number>;
}

export function concatWithLoop<Type>(
  array: Readonly<Array<Type>>,
  ...other: Readonly<Array<Type>>
): Array<Type> {
  if (array.length < other.length) {
    throw new Error("Array length is less than other, can't create loop");
  }

  const reversedOther: Array<Type> = other.slice().reverse();
  let out = [...array, ...reversedOther];
  for (let i = 1; i < other.length; i++) {
    const aLen = array.length;
    const othLen = other.length
    out = out.concat(
      array[aLen - othLen + (i - 1)],
      array[aLen - othLen + i],
      reversedOther[othLen - (i + 1)],
    );
  }

  return out;
}

class RevolutionSolid implements IRevolutionSolid {
  public readonly coordinates: Array<number>;
  constructor(line: Array<vec3>, segmentsCount: number, axis: Axis) {
    let vertices: Array<vec3> = [...line];
    const angleQuant: number = (2 * Math.PI) / segmentsCount;
    for (let angle: number = angleQuant; angle < (2 * Math.PI); angle += angleQuant) {
      const rotated: Array<vec3> = rotateLine(line, angle, axis);
      vertices = concatWithLoop(vertices, ...rotated);
    }
    vertices = concatWithLoop(vertices, ...line);
    this.coordinates = new Array<number>();
    vertices.forEach((vertex: vec3): void => {
      this.coordinates.push(vertex[0]);
      this.coordinates.push(vertex[1]);
      this.coordinates.push(vertex[2]);
    });
  }
};

export function createCone(r: number, h: number, segmentsCount: number): IRevolutionSolid {
  const line = new Array<vec3>(
    new Float32Array([0.0, r, 0.0]),
    new Float32Array([0.0, 0.0, h]),
  );
  return new RevolutionSolid(line, segmentsCount, Axis.Y);
}