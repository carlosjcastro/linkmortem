import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import WatchPanel from "./WatchPanel";
import { WATCH_WORKFLOW } from "./watchWorkflow";

describe("WatchPanel", () => {
  it("copies a workflow that opens pull requests with the Action", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    render(
      <LanguageProvider>
        <WatchPanel />
      </LanguageProvider>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Copy the workflow" }));
    await waitFor(() => expect(writeText).toHaveBeenCalledWith(WATCH_WORKFLOW));
    expect(WATCH_WORKFLOW).toContain("uses: carlosjcastro/linkmortem@main");
    expect(WATCH_WORKFLOW).toContain('open-pull-request: "true"');
    expect(WATCH_WORKFLOW).toContain('open-issue: "true"');
    expect(WATCH_WORKFLOW).toContain("issues: write");
    expect(await screen.findAllByText("Copied")).not.toHaveLength(0);
  });
});
