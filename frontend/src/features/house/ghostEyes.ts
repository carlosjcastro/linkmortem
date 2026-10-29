import { CircleGeometry, Color, InstancedMesh, Matrix4, MeshBasicMaterial, Quaternion, Vector3 } from "three";
import { faceDepth, GHOST_FEATURES } from "../haunting/ghostFeatures";

const HOVER_GROWTH = 0.22;

function rise(intro: number, ghost: number): number {
  const progress = Math.min(1, Math.max(0, intro * 1.4 - ghost * 0.06));
  return progress * progress * (3 - 2 * progress);
}

export function ghostEyes(origins: Vector3[], scale: number, color: string) {
  const geometry = new CircleGeometry(1, 24);
  const material = new MeshBasicMaterial({ color: new Color(color), transparent: true, opacity: 0.9, depthWrite: false, fog: false });
  const eyes = new InstancedMesh(geometry, material, Math.max(1, origins.length * GHOST_FEATURES.length));
  eyes.count = origins.length * GHOST_FEATURES.length;
  eyes.renderOrder = 2;
  eyes.frustumCulled = false;
  const matrix = new Matrix4();
  const place = new Vector3();
  const size = new Vector3();
  const facing = new Quaternion();

  const update = (time: number, intro: number, hovered: number) => {
    origins.forEach((origin, ghost) => {
      const grow = ghost === hovered ? 1 + HOVER_GROWTH : 1;
      const lift = Math.sin(time * 1.1 + ghost * 1.9) * 0.07 - (1 - rise(intro, ghost)) * 0.8;
      GHOST_FEATURES.forEach((feature, index) => {
        place.set(origin.x + feature.x * scale * grow, origin.y + lift + feature.y * scale * grow, origin.z + faceDepth(feature.x) * scale * grow);
        size.set(feature.rx * scale * grow, feature.ry * scale * grow, 1);
        eyes.setMatrixAt(ghost * GHOST_FEATURES.length + index, matrix.compose(place, facing, size));
      });
    });
    eyes.instanceMatrix.needsUpdate = true;
  };

  return { eyes, update, dispose: () => (geometry.dispose(), material.dispose()) };
}
