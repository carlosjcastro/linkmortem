import type { Diagnosis, Verdict } from "./scanTypes";

export function groupResults(
  results: Diagnosis[],
): Record<Verdict, Diagnosis[]> {
  return {
    ghost: results.filter((result) => result.verdict === "ghost"),
    unknown: results.filter((result) => result.verdict === "unknown"),
    alive: results.filter((result) => result.verdict === "alive"),
  };
}
