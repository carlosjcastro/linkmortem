import { ghostAnchor } from "../scan/sectionAnchors";

export function revealGhost(index: number, smooth: boolean): void {
  const item = document.getElementById(ghostAnchor(index));
  if (!item) return;
  item.scrollIntoView({
    behavior: smooth ? "smooth" : "auto",
    block: "center",
  });
  item.querySelector<HTMLElement>("a")?.focus({ preventScroll: true });
}
