import { describe, expect, it } from "vitest";
import { checkTarget } from "./target";

describe("checkTarget", () => {
  it("adds https when the protocol is missing", () => {
    expect(checkTarget("example.com")).toEqual({
      ok: true,
      target: "https://example.com/",
    });
  });

  it("keeps a full GitHub repository address", () => {
    expect(checkTarget(" https://github.com/carlosjcastro/tramo ")).toEqual({
      ok: true,
      target: "https://github.com/carlosjcastro/tramo",
    });
  });

  it.each([
    ["", "invalid"],
    ["ftp://example.com", "invalid"],
    ["javascript:alert(1)", "invalid"],
    ["data:text/html,<script>alert(1)</script>", "invalid"],
    ["localhost", "invalid"],
    ["not a url", "invalid"],
    ["https://example.com/a\nb", "invalid"],
    ["https://user:secret@example.com", "credentials"],
    ["token@example.com", "credentials"],
    ["https://example.com:8080", "port"],
    [`https://example.com/${"a".repeat(300)}`, "length"],
  ])("rejects %s as %s", (input, problem) => {
    expect(checkTarget(input)).toEqual({ ok: false, problem });
  });
});
