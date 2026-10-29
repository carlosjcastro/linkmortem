import { Euler, ExtrudeGeometry, InstancedMesh, Matrix4, type MeshStandardMaterial, Quaternion, Shape, Vector3 } from "three";
import { seededRandom } from "../haunting/random";
import { GRAVE_SLOTS } from "./facade";

const STONE = { half: 0.17, shoulder: 0.3, depth: 0.07 };
const GHOST_HEIGHT = 1.0;

function tombstone(): ExtrudeGeometry {
  const shape = new Shape();
  shape.moveTo(-STONE.half, 0);
  shape.lineTo(-STONE.half, STONE.shoulder);
  shape.absarc(0, STONE.shoulder, STONE.half, Math.PI, 0, true);
  shape.lineTo(STONE.half, 0);
  shape.closePath();
  return new ExtrudeGeometry(shape, { depth: STONE.depth, bevelEnabled: true, bevelThickness: 0.012, bevelSize: 0.012, bevelSegments: 1, curveSegments: 8 });
}

export function graveyard(count: number, material: MeshStandardMaterial) {
  const random = seededRandom(count * 17 + 5);
  const geometry = tombstone();
  const stones = new InstancedMesh(geometry, material, Math.max(1, count));
  stones.count = count;
  const matrix = new Matrix4();
  const origins = GRAVE_SLOTS.slice(0, count).map((slot, index) => {
    const tilt = new Quaternion().setFromEuler(new Euler((random() - 0.6) * 0.16, (random() - 0.5) * 0.5, (random() - 0.5) * 0.22));
    matrix.compose(new Vector3(slot.x, -0.02, slot.z), tilt, new Vector3(1, 0.9 + random() * 0.25, 1));
    stones.setMatrixAt(index, matrix);
    return new Vector3(slot.x, GHOST_HEIGHT, slot.z + 0.05);
  });
  return { stones, origins, dispose: () => geometry.dispose() };
}
