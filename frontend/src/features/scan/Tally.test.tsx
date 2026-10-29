import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LanguageProvider } from "../i18n/LanguageProvider";
import { SECTIONS } from "./sectionAnchors";
import type { Diagnosis, Verdict } from "./scanTypes";
import Tally from "./Tally";

function result(verdict: Verdict, index: number): Diagnosis {
  return {
    link: { url: `https://a.dev/${verdict}/${index}`, source: "x", text: "" },
    verdict,
    cause: "alive",
    status_code: 200,
    final_url: null,
    evidence: "",
  };
}

const groups = {
  ghost: [result("ghost", 1), result("ghost", 2)],
  unknown: [result("unknown", 1)],
  alive: [],
};

describe("Tally", () => {
  it("links each count to its section", () => {
    render(
      <LanguageProvider>
        <Tally groups={groups} />
      </LanguageProvider>,
    );
    expect(screen.getByRole("link", { name: /2\s*dead/ })).toHaveAttribute(
      "href",
      `#${SECTIONS.ghost}`,
    );
    expect(
      screen.getByRole("link", { name: /0\s*still alive/ }),
    ).toHaveAttribute("href", `#${SECTIONS.alive}`);
  });

  it("opens a folded section before jumping to it", () => {
    document.body.insertAdjacentHTML(
      "beforeend",
      `<details id="${SECTIONS.unknown}"><summary>x</summary></details>`,
    );
    render(
      <LanguageProvider>
        <Tally groups={groups} />
      </LanguageProvider>,
    );
    fireEvent.click(screen.getByRole("link", { name: /couldn't confirm/ }));
    expect(
      (document.getElementById(SECTIONS.unknown) as HTMLDetailsElement).open,
    ).toBe(true);
  });
});
