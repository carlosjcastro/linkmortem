export type Slot = { x: number; y: number; z: number; width: number; height: number };

const MAIN_FRONT = 1.31;
const TOWER_FRONT = 1.49;
const WING_FRONT = 0.91;

export const WINDOW_SLOTS: Slot[] = [
  { x: -1.3, y: 0.95, z: MAIN_FRONT, width: 0.44, height: 0.66 },
  { x: 1.3, y: 0.95, z: MAIN_FRONT, width: 0.44, height: 0.66 },
  { x: -0.95, y: 2.15, z: MAIN_FRONT, width: 0.42, height: 0.64 },
  { x: 0, y: 2.15, z: MAIN_FRONT, width: 0.42, height: 0.64 },
  { x: 0.95, y: 2.15, z: MAIN_FRONT, width: 0.42, height: 0.64 },
  { x: 0, y: 3.32, z: MAIN_FRONT, width: 0.36, height: 0.46 },
  { x: 2.15, y: 0.95, z: TOWER_FRONT, width: 0.3, height: 0.6 },
  { x: 2.15, y: 2.15, z: TOWER_FRONT, width: 0.3, height: 0.6 },
  { x: 2.15, y: 3.25, z: TOWER_FRONT, width: 0.3, height: 0.56 },
  { x: -3.15, y: 0.95, z: WING_FRONT, width: 0.4, height: 0.6 },
  { x: -2.3, y: 0.95, z: WING_FRONT, width: 0.4, height: 0.6 },
];

const GRAVE_COLUMNS = [-1.45, 1.45, -2.2, 2.2, -2.95, 2.95, -3.7, 3.7];
const GRAVE_ROWS = [2.8, 3.38];

export const GRAVE_SLOTS = GRAVE_COLUMNS.flatMap((x, column) =>
  GRAVE_ROWS.map((z, row) => ({ x: x + (row ? (column % 2 ? -0.22 : 0.22) : 0), z })),
).sort((first, second) => first.z - second.z || Math.abs(first.x) - Math.abs(second.x));

export const FENCE = { z: 3.95, reach: 4.7, gap: 0.62 };
export const TREE_ROOT = { x: 4.15, z: 0.4 };
export const SCENE_BOUNDS = { left: -4.9, right: 5.6, top: 6.3, target: { x: 0.35, y: 2.05, z: 0.8 } };
