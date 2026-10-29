import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import AfterlifeLine from "./AfterlifeLine";
import type { Afterlife } from "./scanTypes";

const FOUND: Afterlife = {
  status: "found",
  url: "https://learn.dev/space-shooter",
  title: "Space Shooter",
  match: "same",
  evidence: "Build a space shooter",
  source: "graveyard",
};

function renderLine(afterlife: Afterlife | undefined, seeking: boolean) {
  return render(
    <LanguageProvider>
      <AfterlifeLine afterlife={afterlife} seeking={seeking} />
    </LanguageProvider>,
  );
}

describe("AfterlifeLine", () => {
  it("links to the new home with its evidence", () => {
    renderLine(FOUND, false);
    expect(screen.getByRole("link")).toHaveAttribute("href", FOUND.url);
    expect(screen.getByText(/Build a space shooter/)).toBeInTheDocument();
    expect(screen.getByText(/graveyard|cementerio/)).toBeInTheDocument();
  });

  it("stays silent when nothing is being searched", () => {
    const { container } = renderLine(undefined, false);
    expect(container).toBeEmptyDOMElement();
  });

  it("names the closest section of a renamed heading", () => {
    renderLine(
      {
        ...FOUND,
        source: "section",
        title: "#installation",
        url: "https://github.com/o/r/blob/main/GUIDE.md#installation",
        evidence: "",
      },
      false,
    );
    expect(
      screen.getByText("Closest section in the same document"),
    ).toBeInTheDocument();
  });
  it("explains when the daily searches ran out", () => {
    renderLine({ ...FOUND, status: "budget_spent" }, false);
    expect(
      screen.getByText(/web searches for today|búsquedas web por hoy/),
    ).toBeInTheDocument();
  });
  it("credits a move the archived page announced", () => {
    renderLine(
      { ...FOUND, source: "announced", evidence: "Enzyme has moved" },
      false,
    );
    expect(
      screen.getByText(/announced this new address|anunciaba esta dirección/),
    ).toBeInTheDocument();
  });

  it("shows section evidence without quotes", () => {
    renderLine(
      {
        ...FOUND,
        source: "section",
        evidence: "The closest heading is #images.",
      },
      false,
    );
    expect(
      screen.getByText("The closest heading is #images."),
    ).toBeInTheDocument();
  });
});
