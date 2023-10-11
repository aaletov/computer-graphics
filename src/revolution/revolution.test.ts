import { describe, expect, test, beforeEach } from '@jest/globals';
import { vec3 } from 'gl-matrix';
import { Axis, IRevolutionSolid, concatWithLoop, createCone, rotateLine, rotateVertex } from './revolution';

function expectVec3ToBeClose(lhs: vec3, rhs: vec3, precision?: number | undefined): void {
  for (let i = 0; i < lhs.length; i++) {
    expect(lhs[i]).toBeCloseTo(rhs[i], precision);
  }
}

function expectLineToBeClose(lhs: Array<vec3>, rhs: Array<vec3>, precision?: number | undefined): void {
  for (let i = 0; i < lhs.length; i++) {
    expectVec3ToBeClose(lhs[i], rhs[i], precision);
  }
}

describe("rotateVertex", () => {
  let vertex: vec3;
  let expectedVertex: vec3;
  describe("unary vector", () => {
    beforeEach(() => {
      vertex = new Float32Array([1.0, 1.0, 1.0]);
    });
    test("rotate 90 degree around X", () => {
      expectedVertex = new Float32Array([1.0, 1.0, -1.0]);
      const rotatedVertex = rotateVertex(vertex, Math.PI / 2, Axis.X);
      expectVec3ToBeClose(rotatedVertex, expectedVertex);
    });
    test("rotate 90 degree around Y", () => {
      expectedVertex = new Float32Array([-1.0, 1.0, 1.0]);
      const rotatedVertex = rotateVertex(vertex, Math.PI / 2, Axis.Y);
      expectVec3ToBeClose(rotatedVertex, expectedVertex);
    });
    test("rotate 90 degree around Z", () => {
      expectedVertex = new Float32Array([1.0, -1.0, 1.0]);
      const rotatedVertex = rotateVertex(vertex, Math.PI / 2, Axis.Z);
      expectVec3ToBeClose(rotatedVertex, expectedVertex);
    });
  });
});

describe("rotateLine", () => {
  let line: Array<vec3>
  describe("cone generatrix", () => {
    beforeEach(() => {
      line = [
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
      ]
    });
    test("rotate 90 degree around Z", () => {
      const expectedLine = new Array<vec3>(
        [0.0, -1.0, 0.0],
        [0.0, 0.0, 1.0],
      );
      const rotatedLine = rotateLine(line, Math.PI / 2, Axis.Z);
      expectLineToBeClose(rotatedLine, expectedLine);
    });
  })
});

describe("concatWithLoop", () => {
  test("arrays size are equal 2", () => {
    const array = new Array<number>(1, 2);
    const other = new Array<number>(3, 4);
    const expected = new Array<number>(1, 2, 4, 3, 1, 2, 4);
    const concated: Array<number> = concatWithLoop(array, ...other);
    expect(concated).toEqual(expected);
  });
  test("arrays size are equal 4", () => {
    const array = new Array<number>(1, 2, 3, 4);
    const other = new Array<number>(5, 6, 7, 8);
    const expected = new Array<number>(
      1, 2, 3, 4,
      8, 7, 6, 5,
      1, 2, 6,
      2, 3, 7,
      3, 4, 8, 
    );
    const concated: Array<number> = concatWithLoop(array, ...other);
    expect(concated).toEqual(expected);
  })
});
