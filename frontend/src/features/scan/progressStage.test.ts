import { describe, expect, it } from "vitest";
import { dictionaries } from "../i18n/dictionaries";
import { progressStage } from "./progressStage";
import type { Diagnosis, Memory } from "./scanTypes";
import type { ScanState } from "./useScan";

const t = dictionaries.en;
const ghost = { link: { url: "https://a.dev/x", source: "", text: "" }, verdict: "ghost", cause: "not_found", status_code: 404, final_url: null, evidence: "" } as Diagnosis;
const found = { status: "found", archived_url: "", captured_on: "2019-01-01", title: "", excerpt: "" } as Memory;
const base: ScanState = { phase: "checking", target: "", total: 1, results: [], memories: {}, afterlives: {}, reincarnation: true, errorCode: "" };

describe("progressStage", () => {
  it("counts checked links first", () => {
    expect(progressStage(base, t)).toEqual({ label: t.scanChecked(0, 1), value: 0, max: 1 });
  });

  it("moves to the archive and then to new homes", () => {
    const checked = { ...base, results: [ghost] };
    expect(progressStage(checked, t).label).toBe(t.scanRemembering(0, 1));
    expect(progressStage({ ...checked, memories: { "https://a.dev/x": found } }, t).label).toBe(t.scanReincarnating(0, 1));
  });
});
