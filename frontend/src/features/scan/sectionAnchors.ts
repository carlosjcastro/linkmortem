export const SECTIONS = {
  ghost: "ghosts",
  unknown: "unconfirmed",
  alive: "alive",
} as const;

export function ghostAnchor(index: number): string {
  return `ghost-${index}`;
}

export function openSection(id: string): void {
  const section = document.getElementById(id);
  if (section instanceof HTMLDetailsElement) section.open = true;
}
