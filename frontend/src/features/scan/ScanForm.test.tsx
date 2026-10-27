import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
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
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "example.com" } });
    fireEvent.click(screen.getByRole("button"));
    expect(onScan).toHaveBeenCalledWith("https://example.com/");
  });

  it("announces an invalid address", () => {
    const onScan = renderForm();
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "nothing" } });
    fireEvent.click(screen.getByRole("button"));
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(onScan).not.toHaveBeenCalled();
  });
});
