import { CircleGeometry, Color, Group, Mesh, MeshBasicMaterial } from "three";

const FEATURES = [
  { x: -0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0, y: 0.04, rx: 0.11, ry: 0.15 },
];
const FACE_DEPTH = 1.02;

export function ghostFace(color: string): { face: Group; dispose: () => void } {
  const geometry = new CircleGeometry(1, 40);
  const material = new MeshBasicMaterial({
    color: new Color(color),
    transparent: true,
    opacity: 0.92,
    depthWrite: false,
  });
  const face = new Group();
  for (const feature of FEATURES) {
    const socket = new Mesh(geometry, material);
    socket.position.set(
      feature.x,
      feature.y,
      FACE_DEPTH * Math.cos(Math.asin(feature.x)) * 0.92,
    );
    socket.scale.set(feature.rx, feature.ry, 1);
    socket.renderOrder = 2;
    face.add(socket);
  }
  return { face, dispose: () => (geometry.dispose(), material.dispose()) };
}
