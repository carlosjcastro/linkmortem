import type { BufferGeometry } from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";

export function mergeSolids(parts: BufferGeometry[]): BufferGeometry {
  const flat = parts.map((part) => (part.index ? part.toNonIndexed() : part));
  const merged = mergeGeometries(flat);
  new Set([...parts, ...flat]).forEach((part) => part.dispose());
  return merged;
}
