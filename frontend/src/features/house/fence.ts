import { BoxGeometry, Group, InstancedMesh, Matrix4, Mesh, type MeshStandardMaterial, Vector3 } from "three";
import { FENCE } from "./facade";
import { mergeSolids } from "./mergeSolids";

const SPACING = 0.24;
const PICKET = { width: 0.055, height: 0.62, depth: 0.03 };

export function fence(material: MeshStandardMaterial) {
  const xs: number[] = [];
  for (let x = -FENCE.reach; x <= FENCE.reach + 0.001; x += SPACING) {
    if (Math.abs(x) > FENCE.gap) xs.push(x);
  }
  const picket = new BoxGeometry(PICKET.width, PICKET.height, PICKET.depth);
  const pickets = new InstancedMesh(picket, material, xs.length);
  const matrix = new Matrix4();
  xs.forEach((x, index) => {
    const lean = Math.sin(x * 7.3) * 0.06;
    matrix.makeRotationZ(lean).setPosition(new Vector3(x, PICKET.height / 2 - 0.02, FENCE.z));
    pickets.setMatrixAt(index, matrix);
  });
  const railLength = FENCE.reach - FENCE.gap;
  const railCenter = (FENCE.reach + FENCE.gap) / 2;
  const rails = new Mesh(
    mergeSolids(
      [-railCenter, railCenter].flatMap((x) =>
        [0.16, 0.44].map((y) => new BoxGeometry(railLength, 0.035, 0.025).translate(x, y, FENCE.z - 0.025)),
      ),
    ),
    material,
  );
  const group = new Group();
  group.add(pickets, rails);
  return { group, dispose: () => (picket.dispose(), rails.geometry.dispose()) };
}
