import type { HauntingColors } from "./createScene";

export function readColors(element: HTMLElement): HauntingColors {
  const style = getComputedStyle(element);
  return {
    spirit: style.getPropertyValue("--spectral").trim() || "#a8e6df",
    marigold: style.getPropertyValue("--marigold").trim() || "#f4a23c",
    night: style.getPropertyValue("--night").trim() || "#1b1430",
    bone: style.getPropertyValue("--bone").trim() || "#efe6d8",
  };
}
