import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import SourceLine from "./SourceLine";

const blob = "https://github.com/owner/repo/blob/main";

function renderLine(other_sources: string[]) {
  render(
    <LanguageProvider>
      <SourceLine
        link={{
          url: "https://gone.dev",
          source: `${blob}/README.md`,
          text: "",
          other_sources,
        }}
      />
    </LanguageProvider>,
  );
}

describe("SourceLine", () => {
  it("links every file that holds the same dead link", () => {
    renderLine([`${blob}/docs/guide.md`]);
    expect(screen.getByRole("link", { name: "README.md" })).toHaveAttribute(
      "href",
      `${blob}/README.md`,
    );
    expect(
      screen.getByRole("link", { name: "docs/guide.md" }),
    ).toBeInTheDocument();
  });

  it("counts the files beyond the first three", () => {
    renderLine(["a", "b", "c", "d"].map((name) => `${blob}/${name}.md`));
    expect(screen.getAllByRole("link")).toHaveLength(3);
    expect(screen.getByText(/and 2 more/)).toBeInTheDocument();
  });
});
