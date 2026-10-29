export const GHOST_FEATURES = [
  { x: -0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0, y: 0.04, rx: 0.11, ry: 0.15 },
];

export const FACE_DEPTH = 1.02;

export function faceDepth(x: number): number {
  return FACE_DEPTH * Math.cos(Math.asin(x)) * 0.92;
}
