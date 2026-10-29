import type { Diagnosis } from "./scanTypes";

export function needsMemory(result: Diagnosis): boolean {
  return result.verdict === "ghost" && result.cause !== "missing_section";
}
