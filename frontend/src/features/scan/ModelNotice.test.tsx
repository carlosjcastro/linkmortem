import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import ModelNotice from "./ModelNotice";
import type { Cause, Diagnosis } from "./scanTypes";

function result(cause: Cause): Diagnosis {
  return { link: { url: `https://a.dev/${cause}`, source: "x", text: "" }, verdict: "unknown", cause, status_code: 200, final_url: null, evidence: "" };
}

function renderNotice(results: Diagnosis[]) {
  return render(
    <LanguageProvider>
      <ModelNotice results={results} />
    </LanguageProvider>,
  );
}

describe("ModelNotice", () => {
  it("counts the pages Gemma couldn't read", () => {
    renderNotice([result("model_unavailable"), result("model_unavailable"), result("timeout")]);
    expect(screen.getByText(/2 pages that looked suspicious stay unconfirmed/)).toBeInTheDocument();
  });

  it("stays silent when Gemma answered", () => {
    const { container } = renderNotice([result("unclassified")]);
    expect(container).toBeEmptyDOMElement();
  });
});
