import {
  BoxGeometry,
  type BufferGeometry,
  ConeGeometry,
  CylinderGeometry,
  EdgesGeometry,
  ExtrudeGeometry,
  Group,
  LineBasicMaterial,
  LineSegments,
  Mesh,
  type MeshStandardMaterial,
  Shape,
  Vector2,
} from "three";
import { mergeSolids } from "./mergeSolids";

const TOWER = { x: 2.15, z: 0.9, radius: 0.62, height: 3.9 };

function box(
  width: number,
  height: number,
  depth: number,
  x: number,
  y: number,
  z: number,
): BufferGeometry {
  return new BoxGeometry(width, height, depth).translate(x, y, z);
}

function gable(half: number, rise: number, length: number): BufferGeometry {
  const shape = new Shape([
    new Vector2(-half, 0),
    new Vector2(half, 0),
    new Vector2(0, rise),
  ]);
  return new ExtrudeGeometry(shape, {
    depth: length,
    bevelEnabled: false,
  }).translate(0, 0, -length / 2);
}

function walls(): BufferGeometry {
  return mergeSolids([
    box(3.6, 2.8, 2.6, 0, 1.4, 0),
    box(1.95, 1.9, 1.8, -2.75, 0.95, 0),
    new CylinderGeometry(TOWER.radius, TOWER.radius, TOWER.height, 8)
      .rotateY(Math.PI / 8)
      .translate(TOWER.x, TOWER.height / 2, TOWER.z),
    box(0.36, 1.5, 0.36, -1.0, 3.8, -0.5),
    box(2.3, 0.18, 0.95, 0, 0.09, 1.76),
    box(0.9, 0.09, 0.32, 0, 0.045, 2.38),
  ]);
}

function roofs(): BufferGeometry {
  return mergeSolids([
    gable(2.05, 1.45, 2.95).translate(0, 2.8, 0),
    gable(1.08, 0.78, 2.05)
      .rotateY(Math.PI / 2)
      .translate(-2.7, 1.9, 0),
    new ConeGeometry(0.82, 1.85, 8)
      .rotateY(Math.PI / 8)
      .translate(TOWER.x, TOWER.height + 0.92, TOWER.z),
    new CylinderGeometry(0.015, 0.03, 0.55, 4).translate(
      TOWER.x,
      TOWER.height + 2.1,
      TOWER.z,
    ),
    box(2.55, 0.08, 1.12, 0, 1.5, 1.82),
    box(0.09, 1.25, 0.09, -1.08, 0.8, 2.18),
    box(0.09, 1.25, 0.09, 1.08, 0.8, 2.18),
    box(0.62, 1.12, 0.05, 0, 0.74, 1.31),
    box(0.46, 0.06, 0.06, 0, 4.58, -0.5),
  ]);
}

export function houseBody(
  wallMaterial: MeshStandardMaterial,
  roofMaterial: MeshStandardMaterial,
  edgeColor: string,
) {
  const wallGeometry = walls();
  const roofGeometry = roofs();
  const edgeMaterial = new LineBasicMaterial({
    color: edgeColor,
    transparent: true,
    opacity: 0.16,
  });
  const edges = [
    new EdgesGeometry(wallGeometry, 30),
    new EdgesGeometry(roofGeometry, 30),
  ];
  const group = new Group();
  group.add(
    new Mesh(wallGeometry, wallMaterial),
    new Mesh(roofGeometry, roofMaterial),
    ...edges.map((edge) => new LineSegments(edge, edgeMaterial)),
  );
  return {
    group,
    dispose: () =>
      [wallGeometry, roofGeometry, ...edges, edgeMaterial].forEach((item) =>
        item.dispose(),
      ),
  };
}
