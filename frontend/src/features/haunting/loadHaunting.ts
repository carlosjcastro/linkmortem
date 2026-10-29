import type { Haunting } from "./createScene";
import { readColors } from "./readColors";

export async function loadHaunting(
  canvas: HTMLCanvasElement,
): Promise<Haunting> {
  const { createScene } = await import("./createScene");
  return createScene(canvas, readColors(document.documentElement));
}
