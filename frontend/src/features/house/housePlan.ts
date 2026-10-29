import { seededRandom } from "../haunting/random";

export const WINDOW_STATES = { alive: 0, dead: 1, unknown: 2 } as const;
export const MAX_GRAVES = 12;

export type HouseCounts = { alive: number; ghost: number; unknown: number };
export type HousePlan = { windows: number[]; graves: number };

function shares(counts: HouseCounts, slots: number): Record<keyof typeof WINDOW_STATES, number> {
  const parts = { alive: counts.alive, dead: counts.ghost, unknown: counts.unknown };
  const total = parts.alive + parts.dead + parts.unknown;
  if (total === 0) return { alive: 0, dead: slots, unknown: 0 };
  const names = Object.keys(parts) as (keyof typeof parts)[];
  const exact = names.map((name) => ({ name, value: (parts[name] * slots) / total }));
  const result = Object.fromEntries(exact.map(({ name, value }) => [name, parts[name] ? Math.max(1, Math.floor(value)) : 0])) as Record<keyof typeof parts, number>;
  const byRemainder = [...exact].sort((first, second) => (second.value % 1) - (first.value % 1));
  let left = slots - names.reduce((sum, name) => sum + result[name], 0);
  for (let index = 0; left > 0; index = (index + 1) % names.length) {
    const name = byRemainder[index].name;
    if (parts[name]) {
      result[name] += 1;
      left -= 1;
    }
  }
  while (left < 0) {
    const largest = names.reduce((best, name) => (result[name] > result[best] ? name : best));
    result[largest] -= 1;
    left += 1;
  }
  return result;
}

function shuffled(values: number[], seed: number): number[] {
  const random = seededRandom(seed);
  const result = [...values];
  for (let index = result.length - 1; index > 0; index -= 1) {
    const other = Math.floor(random() * (index + 1));
    [result[index], result[other]] = [result[other], result[index]];
  }
  return result;
}

export function housePlan(counts: HouseCounts, slots: number): HousePlan {
  const split = shares(counts, slots);
  const states = (Object.keys(split) as (keyof typeof split)[]).flatMap((name) => Array<number>(split[name]).fill(WINDOW_STATES[name]));
  return { windows: shuffled(states, counts.alive * 7 + counts.ghost * 13 + counts.unknown), graves: Math.min(counts.ghost, MAX_GRAVES) };
}
