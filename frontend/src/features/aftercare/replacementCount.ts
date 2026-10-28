import type { ScanState } from "../scan/scanState";

const REPOSITORY = /^https?:\/\/(www\.)?github\.com\/[\w.-]+\/[\w.-]+/;

export function isRepositoryScan(target: string): boolean {
  return REPOSITORY.test(target);
}

export function replacementCount(state: ScanState): number {
  return state.results.filter((result) => {
    if (result.verdict !== "ghost") return false;
    const url = result.link.url;
    return state.afterlives[url]?.status === "found" || state.memories[url]?.status === "found";
  }).length;
}

export function livingCount(state: ScanState): number {
  return state.results.filter((result) => result.verdict === "alive").length;
}
