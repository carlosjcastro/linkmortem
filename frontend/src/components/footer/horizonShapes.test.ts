import { describe, expect, it } from "vitest";
import { picketPositions, stonePath } from "./horizonShapes";

describe("horizonShapes", () => {
  it("draws an arched stone that stands on its base", () => {
    expect(stonePath({ x: 10, width: 20, height: 30, tilt: 0 }, 100)).toBe(
      "M10 100V80A10 10 0 0 1 30 80V100Z",
    );
  });

  it("spaces fence pickets evenly from end to end", () => {
    expect(picketPositions(0, 30, 15)).toEqual([0, 15, 30]);
  });
});
