import { describe, expect, it } from "vitest";
import { INITIAL_SCAN } from "../scan/scanState";
import type { Diagnosis } from "../scan/scanTypes";
import { isRepositoryScan, livingCount, replacementCount } from "./replacementCount";

function result(url: string, verdict: Diagnosis["verdict"]): Diagnosis {
  return { link: { url, source: "", text: "" }, verdict, cause: verdict === "ghost" ? "not_found" : "alive", status_code: null, final_url: null, evidence: "" };
}

describe("aftercare counts", () => {
  it("counts ghosts that have a replacement and living links", () => {
    const state = {
      ...INITIAL_SCAN,
      results: [result("https://a.dev/1", "ghost"), result("https://a.dev/2", "ghost"), result("https://b.dev", "alive")],
      memories: { "https://a.dev/1": { status: "found", archived_url: "", captured_on: "2019-01-01", title: "", excerpt: "" } },
    } as typeof INITIAL_SCAN;
    expect(replacementCount(state)).toBe(1);
    expect(livingCount(state)).toBe(1);
  });

  it("offers patches only for repositories", () => {
    expect(isRepositoryScan("https://github.com/owner/repo")).toBe(true);
    expect(isRepositoryScan("https://example.com")).toBe(false);
  });
});
