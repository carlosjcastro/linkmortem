import { describe, expect, it } from "vitest";
import { sourceLabel } from "./sourceLabel";

describe("sourceLabel", () => {
  it("shows the path of a repository file", () => {
    expect(
      sourceLabel(
        "https://github.com/owner/repo/blob/main/docs/Getting%20started.md",
      ),
    ).toBe("docs/Getting started.md");
  });

  it("keeps a website address as it is", () => {
    expect(sourceLabel("https://site.dev/about")).toBe(
      "https://site.dev/about",
    );
  });
});
