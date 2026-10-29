import { CircleGeometry, Color, Group, Mesh, MeshBasicMaterial } from "three";
import { faceDepth, GHOST_FEATURES } from "./ghostFeatures";

export function ghostFace(color: string): { face: Group; dispose: () => void } {
  const geometry = new CircleGeometry(1, 40);
  const material = new MeshBasicMaterial({
    color: new Color(color),
    transparent: true,
    opacity: 0.92,
    depthWrite: false,
  });
  const face = new Group();
  for (const feature of GHOST_FEATURES) {
    const socket = new Mesh(geometry, material);
    socket.position.set(feature.x, feature.y, faceDepth(feature.x));
    socket.scale.set(feature.rx, feature.ry, 1);
    socket.renderOrder = 2;
    face.add(socket);
  }
  return { face, dispose: () => (geometry.dispose(), material.dispose()) };
}
