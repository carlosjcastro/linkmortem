import { seededRandom } from "./random";

const HEAD_CENTER = 0.3;
const HEAD_RADIUS = 0.95;
const HEM_LEVEL = -1.25;
const EYES = [
  { x: -0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0.34, y: 0.52, rx: 0.15, ry: 0.23 },
  { x: 0, y: 0.04, rx: 0.11, ry: 0.15 },
];

export type GhostBuffers = {
  targets: Float32Array;
  scatter: Float32Array;
  seeds: Float32Array;
};

function radiusAt(y: number): number {
  if (y > HEAD_CENTER)
    return Math.sqrt(Math.max(0, HEAD_RADIUS ** 2 - (y - HEAD_CENTER) ** 2));
  return HEAD_RADIUS + 0.14 * (HEAD_CENTER - y);
}

function insideFace(x: number, y: number, z: number): boolean {
  return (
    z > 0 &&
    EYES.some(
      (eye) => ((x - eye.x) / eye.rx) ** 2 + ((y - eye.y) / eye.ry) ** 2 < 1,
    )
  );
}

export function ghostPoints(count: number): GhostBuffers {
  const random = seededRandom(1031);
  const targets = new Float32Array(count * 3);
  const scatter = new Float32Array(count * 3);
  const seeds = new Float32Array(count);
  let filled = 0;

  while (filled < count) {
    const y = HEM_LEVEL + random() * (HEAD_CENTER + HEAD_RADIUS - HEM_LEVEL);
    const angle = random() * Math.PI * 2;
    const hem = HEM_LEVEL + 0.13 * Math.sin(angle * 6) + 0.13;
    const radius = radiusAt(y) * (0.9 + 0.1 * Math.sqrt(random()));
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    if (y < hem || insideFace(x, y, z)) continue;

    const index = filled * 3;
    targets.set([x, y, z], index);
    const spread = 4 + random() * 5;
    const theta = random() * Math.PI * 2;
    const phi = Math.acos(2 * random() - 1);
    scatter.set(
      [
        spread * Math.sin(phi) * Math.cos(theta),
        spread * Math.cos(phi),
        spread * Math.sin(phi) * Math.sin(theta),
      ],
      index,
    );
    seeds[filled] = random();
    filled += 1;
  }

  return { targets, scatter, seeds };
}
