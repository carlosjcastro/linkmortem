import { describe, expect, it } from "vitest";
import { applyEvent, INITIAL_SCAN } from "./scanState";
import { sharedScanId } from "./savedScan";
import type { ScanEvent } from "./scanTypes";

describe("scan state", () => {
  it("replays a saved scan into the same state a live scan builds", () => {
    const events: ScanEvent[] = [
      { type: "collected", total: 1, reincarnation: false },
      { type: "link", diagnosis: { link: { url: "https://a.dev/x", source: "", text: "" }, verdict: "ghost", cause: "not_found", status_code: 404, final_url: null, evidence: "" } },
      { type: "done", summary: { ghost: 1 } },
      { type: "saved", id: "abc123def4" },
    ];
    const state = events.reduce(applyEvent, INITIAL_SCAN);
    expect(state.phase).toBe("done");
    expect(state.results).toHaveLength(1);
    expect(state.shareId).toBe("abc123def4");
  });

  it("reads share ids only from share paths", () => {
    expect(sharedScanId("/r/abc123def4")).toBe("abc123def4");
    expect(sharedScanId("/r/../../etc")).toBe("");
    expect(sharedScanId("/")).toBe("");
  });
});
