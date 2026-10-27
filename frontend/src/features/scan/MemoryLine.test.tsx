import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import MemoryLine from "./MemoryLine";
import type { Memory } from "./scanTypes";

const FOUND: Memory = {
  status: "found",
  archived_url: "https://web.archive.org/web/20190303000000/https://a.dev/docs",
  captured_on: "2019-03-03",
  title: "Install guide",
  excerpt: "Run the installer.",
};

function renderLine(memory: Memory | undefined, remembering: boolean) {
  render(
    <LanguageProvider>
      <MemoryLine memory={memory} remembering={remembering} />
    </LanguageProvider>,
  );
}

describe("MemoryLine", () => {
  it("links to the last healthy copy with its date", () => {
    renderLine(FOUND, false);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", FOUND.archived_url);
    expect(link).toHaveTextContent("2019");
    expect(screen.getByText("Install guide")).toBeInTheDocument();
  });

  it("shows the search only while the scan runs", () => {
    renderLine(undefined, true);
    expect(screen.getByText(/Wayback Machine/)).toBeInTheDocument();
  });

  it("stays silent after the scan without a memory", () => {
    const { container } = render(
      <LanguageProvider>
        <MemoryLine remembering={false} />
      </LanguageProvider>,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
