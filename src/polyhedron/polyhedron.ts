export function getDodecahedronPolarCoordinates(R: Number): Array<Array<Number>> {
  const RADIAN_DEGREE = Math.PI / 180;
  const ALPHA = Math.asin(Math.sqrt(3) / 3);
  const BETA = Math.acos(Math.sqrt(3) / (6 * Math.sin(54 * RADIAN_DEGREE)));
  return [
    [R, (Math.PI / 4) + 0*(Math.PI / 2), ALPHA],
    [R, (Math.PI / 4) + 1*(Math.PI / 2), ALPHA],
    [R, (Math.PI / 4) + 2*(Math.PI / 2), ALPHA],
    [R, (Math.PI / 4) + 3*(Math.PI / 2), ALPHA],
    [R, (Math.PI / 4) + 0 * (Math.PI / 2), -ALPHA],
    [R, (Math.PI / 4) + 1 * (Math.PI / 2), -ALPHA],
    [R, (Math.PI / 4) + 2 * (Math.PI / 2), -ALPHA],
    [R, (Math.PI / 4) + 3 * (Math.PI / 2), -ALPHA],
    [R, BETA, 0],
    [R, Math.PI - BETA, 0],
    [R, Math.PI + BETA, 0],
    [R, -BETA, 0],
    [R, Math.PI / 2, BETA],
    [R, Math.PI / 2, Math.PI - BETA],
    [R, Math.PI / 2, Math.PI + BETA],
    [R, Math.PI / 2, -BETA],
    [R, 2 * Math.PI, (Math.PI - BETA)],
    [R, 2 * Math.PI, -(Math.PI - BETA)],
    [R, Math.PI, (Math.PI - BETA)],
    [R, Math.PI, -(Math.PI - BETA)],
  ];
}