import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import ShareLink from "./ShareLink";

function renderShare() {
  render(
    <LanguageProvider>
      <ShareLink id="abc123abc123" />
    </LanguageProvider>,
  );
}

describe("ShareLink", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("confirms a copied link", async () => {
    vi.stubGlobal("navigator", {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    });
    renderShare();
    fireEvent.click(screen.getByRole("button", { name: "Copy link" }));
    expect(
      await screen.findByRole("button", { name: "Link copied" }),
    ).toBeInTheDocument();
  });

  it("says so when the browser refuses to copy", async () => {
    vi.stubGlobal("navigator", {
      clipboard: { writeText: vi.fn().mockRejectedValue(new Error("denied")) },
    });
    renderShare();
    fireEvent.click(screen.getByRole("button", { name: "Copy link" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "didn't allow copying",
    );
  });
});
