import { describe, expect, it } from "vitest";
import { housePlan, MAX_GRAVES, WINDOW_STATES } from "./housePlan";

const lit = (windows: number[], state: number) => windows.filter((window) => window === state).length;

describe("housePlan", () => {
  it("lights the windows in proportion to the links", () => {
    const { windows } = housePlan({ alive: 129, ghost: 7, unknown: 14 }, 11);
    expect(windows).toHaveLength(11);
    expect(lit(windows, WINDOW_STATES.alive)).toBe(9);
    expect(lit(windows, WINDOW_STATES.dead)).toBe(1);
    expect(lit(windows, WINDOW_STATES.unknown)).toBe(1);
  });

  it("never hides a kind of link that exists", () => {
    const { windows } = housePlan({ alive: 600, ghost: 1, unknown: 1 }, 11);
    expect(lit(windows, WINDOW_STATES.dead)).toBe(1);
    expect(lit(windows, WINDOW_STATES.unknown)).toBe(1);
  });

  it("gives every dead link a grave up to the limit", () => {
    expect(housePlan({ alive: 1, ghost: 3, unknown: 0 }, 11).graves).toBe(3);
    expect(housePlan({ alive: 1, ghost: 40, unknown: 0 }, 11).graves).toBe(MAX_GRAVES);
  });

  it("draws the same house for the same scan", () => {
    expect(housePlan({ alive: 5, ghost: 2, unknown: 1 }, 11)).toEqual(housePlan({ alive: 5, ghost: 2, unknown: 1 }, 11));
  });
});
