export const HORIZON_WIDTH = 1440;
export const HORIZON_HEIGHT = 120;

export type Stone = { x: number; width: number; height: number; tilt: number };

export const GROUND =
  "M0 120V100C200 90 380 104 620 98C860 92 1080 106 1300 96C1370 93 1410 95 1440 96V120Z";

export const STONES: Stone[] = [
  { x: 96, width: 30, height: 40, tilt: -4 },
  { x: 150, width: 22, height: 28, tilt: 3 },
  { x: 410, width: 34, height: 46, tilt: 0 },
  { x: 462, width: 24, height: 30, tilt: -6 },
  { x: 760, width: 28, height: 36, tilt: 5 },
  { x: 1310, width: 32, height: 42, tilt: -3 },
  { x: 1362, width: 20, height: 26, tilt: 7 },
];

export const CROSSES = [
  { x: 250, height: 44 },
  { x: 640, height: 38 },
];

export const FENCE = { from: 930, to: 1230, gap: 15, height: 34, base: 102 };

export function stonePath({ x, width, height }: Stone, base: number): string {
  const radius = width / 2;
  const shoulder = base - height + radius;
  return `M${x} ${base}V${shoulder}A${radius} ${radius} 0 0 1 ${x + width} ${shoulder}V${base}Z`;
}

export function picketPositions(
  from: number,
  to: number,
  gap: number,
): number[] {
  const count = Math.floor((to - from) / gap) + 1;
  return Array.from({ length: count }, (_, index) => from + index * gap);
}

export function picketPath(x: number, base: number, height: number): string {
  const top = base - height;
  return `M${x - 1.5} ${base}V${top}L${x} ${top - 6}L${x + 1.5} ${top}V${base}Z`;
}
