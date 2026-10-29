import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import CoverageNote from "./CoverageNote";
import type { Coverage } from "./scanTypes";

function renderNote(total: number, coverage: Coverage) {
  return render(
    <LanguageProvider>
      <CoverageNote total={total} coverage={coverage} />
    </LanguageProvider>,
  );
}

describe("CoverageNote", () => {
  it("says which links and files a capped scan left out", () => {
    renderNote(150, {
      found: 412,
      read: 40,
      available: 87,
      source: "repository",
    });
    expect(screen.getByText(/first 150 of the 412 links/)).toBeInTheDocument();
    expect(screen.getByText(/40 of the 87 Markdown files/)).toBeInTheDocument();
  });

  it("stays silent when the scan covered everything", () => {
    const { container } = renderNote(12, {
      found: 12,
      read: 3,
      available: 3,
      source: "site",
    });
    expect(container).toBeEmptyDOMElement();
  });
});
