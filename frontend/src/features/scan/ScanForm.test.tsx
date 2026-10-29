import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import { EXAMPLE_TARGET } from "../../lib/example";
import ScanForm from "./ScanForm";

function renderForm() {
  const onScan = vi.fn();
  render(
    <LanguageProvider>
      <ScanForm onScan={onScan} />
    </LanguageProvider>,
  );
  return onScan;
}

describe("ScanForm", () => {
  it("sends a normalized address", () => {
    const onScan = renderForm();
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Find dead links" }));
    expect(onScan).toHaveBeenCalledWith("https://example.com/");
  });

  it("announces an invalid address", () => {
    const onScan = renderForm();
    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "nothing" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Find dead links" }));
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(onScan).not.toHaveBeenCalled();
  });

  it("scans the demo repository in one click and shows it", () => {
    const onScan = renderForm();
    fireEvent.click(screen.getByRole("button", { name: /demo repository/ }));
    expect(onScan).toHaveBeenCalledWith(EXAMPLE_TARGET);
    expect(screen.getByRole("textbox")).toHaveValue(EXAMPLE_TARGET);
  });
});
