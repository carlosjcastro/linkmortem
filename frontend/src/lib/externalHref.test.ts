import { describe, expect, it } from "vitest";
import { externalHref } from "./externalHref";

describe("externalHref", () => {
  it("keeps web addresses", () => {
    expect(externalHref("https://a.dev/x")).toBe("https://a.dev/x");
  });

  it.each(["javascript:alert(1)", "data:text/html,x", "not a url", ""])(
    "drops %s",
    (address) => {
      expect(externalHref(address)).toBeUndefined();
    },
  );
});
