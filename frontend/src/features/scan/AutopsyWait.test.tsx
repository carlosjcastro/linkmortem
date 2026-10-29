import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import AutopsyWait from "./AutopsyWait";

describe("AutopsyWait", () => {
  it("says a saved autopsy is loading, not a new scan", () => {
    render(
      <LanguageProvider>
        <AutopsyWait />
      </LanguageProvider>,
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      "Raising this autopsy from the graveyard",
    );
    expect(
      screen.getByText(/Nothing is being scanned again/),
    ).toBeInTheDocument();
  });
});
