import { describe, expect, it } from "vitest";
import { groupResults } from "./groupResults";
import type { Diagnosis, Verdict } from "./scanTypes";

const result = (url: string, verdict: Verdict): Diagnosis => ({
  link: { url, source: "https://a.dev", text: "" },
  verdict,
  cause: verdict === "ghost" ? "not_found" : "alive",
  status_code: null,
  final_url: null,
  evidence: "",
});

describe("groupResults", () => {
  it("separates ghosts, unconfirmed and living links", () => {
    const groups = groupResults([
      result("a", "ghost"),
      result("b", "alive"),
      result("c", "unknown"),
      result("d", "ghost"),
    ]);
    expect(groups.ghost.map((item) => item.link.url)).toEqual(["a", "d"]);
    expect(groups.unknown).toHaveLength(1);
    expect(groups.alive).toHaveLength(1);
  });
});
