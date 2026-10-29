import {
  type BufferGeometry,
  CylinderGeometry,
  Mesh,
  type MeshStandardMaterial,
  Quaternion,
  Vector3,
} from "three";
import { seededRandom } from "../haunting/random";
import { TREE_ROOT } from "./facade";
import { mergeSolids } from "./mergeSolids";

const UP = new Vector3(0, 1, 0);
const DEPTH = 4;

function grow(
  random: () => number,
  start: Vector3,
  direction: Vector3,
  length: number,
  radius: number,
  depth: number,
  parts: BufferGeometry[],
) {
  const end = start.clone().addScaledVector(direction, length);
  const limb = new CylinderGeometry(radius * 0.62, radius, length, 5, 1);
  limb.applyQuaternion(new Quaternion().setFromUnitVectors(UP, direction));
  limb.translate(
    (start.x + end.x) / 2,
    (start.y + end.y) / 2,
    (start.z + end.z) / 2,
  );
  parts.push(limb);
  if (depth === 0) return;
  const children = random() < 0.45 ? 3 : 2;
  for (let child = 0; child < children; child += 1) {
    const axis = new Vector3(random() - 0.5, 0, random() - 0.5).normalize();
    const bend = new Quaternion().setFromAxisAngle(axis, 0.4 + random() * 0.5);
    const next = direction
      .clone()
      .applyQuaternion(bend)
      .add(new Vector3(0, 0.12, 0))
      .normalize();
    grow(
      random,
      end,
      next,
      length * (0.62 + random() * 0.14),
      radius * 0.6,
      depth - 1,
      parts,
    );
  }
}

export function deadTree(material: MeshStandardMaterial): Mesh {
  const parts: BufferGeometry[] = [];
  grow(
    seededRandom(77),
    new Vector3(TREE_ROOT.x, 0, TREE_ROOT.z),
    new Vector3(-0.12, 1, 0.05).normalize(),
    1.55,
    0.16,
    DEPTH,
    parts,
  );
  return new Mesh(mergeSolids(parts), material);
}
