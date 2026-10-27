import { readValue, writeValue } from "../../lib/storage";

const STORAGE_KEY = "linkmortem.motion";
const REDUCED_QUERY = "(prefers-reduced-motion: reduce)";

export function initialMotion(): boolean {
  const saved = readValue(STORAGE_KEY);
  if (saved !== null) return saved === "on";
  return !window.matchMedia(REDUCED_QUERY).matches;
}

export function saveMotion(enabled: boolean): void {
  writeValue(STORAGE_KEY, enabled ? "on" : "off");
}
