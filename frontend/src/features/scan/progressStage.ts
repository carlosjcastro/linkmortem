import type { Dictionary } from "../i18n/dictionaries";
import { needsMemory } from "./needsMemory";
import type { ScanState } from "./scanState";

export type ProgressStage = { label: string; value?: number; max?: number };

export function progressStage(state: ScanState, t: Dictionary): ProgressStage {
  if (state.phase === "collecting") return { label: t.scanCollecting };
  const checked = state.results.length;
  const ghosts = state.results.filter(needsMemory).length;
  if (checked < state.total || ghosts === 0)
    return {
      label: t.scanChecked(checked, state.total),
      value: checked,
      max: state.total,
    };
  const remembered = Object.keys(state.memories).length;
  const seekable = Object.values(state.memories).filter(
    (memory) => memory.status === "found",
  ).length;
  if (remembered < ghosts || !state.reincarnation || seekable === 0)
    return {
      label: t.scanRemembering(remembered, ghosts),
      value: remembered,
      max: ghosts,
    };
  const sought = Object.keys(state.afterlives).length;
  return {
    label: t.scanReincarnating(sought, seekable),
    value: sought,
    max: seekable,
  };
}
