import { readColors } from "../haunting/readColors";
import type { HouseScene } from "./createHouse";
import type { HousePlan } from "./housePlan";

export async function loadHouse(
  canvas: HTMLCanvasElement,
  plan: HousePlan,
): Promise<HouseScene> {
  const { createHouse } = await import("./createHouse");
  return createHouse(canvas, readColors(document.documentElement), plan);
}
