import { describe, expect, it } from "vitest";
import { normalizeTarget } from "./target";

describe("normalizeTarget", () => {
  it("adds https when the protocol is missing", () => {
    expect(normalizeTarget("example.com")).toBe("https://example.com/");
  });

  it("keeps a full GitHub repository address", () => {
    expect(normalizeTarget(" https://github.com/carlosjcastro/tramo ")).toBe(
      "https://github.com/carlosjcastro/tramo",
    );
  });

  it.each(["", "   ", "ftp://example.com", "localhost", "not a url"])(
    "rejects %s",
    (input) => {
      expect(normalizeTarget(input)).toBeNull();
    },
  );
});
