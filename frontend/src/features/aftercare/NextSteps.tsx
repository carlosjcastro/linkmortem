import type { ReactNode } from "react";
import { useTranslation } from "../i18n/useTranslation";
import type { ScanState } from "../scan/scanState";
import ShareLink from "../scan/ShareLink";
import PreservePanel from "./PreservePanel";
import RestPanel from "./RestPanel";
import {
  isRepositoryScan,
  livingCount,
  replacementCount,
} from "./replacementCount";

export default function NextSteps({ state }: { state: ScanState }) {
  const { t } = useTranslation();
  const replacements = isRepositoryScan(state.target)
    ? replacementCount(state)
    : 0;
  const living = livingCount(state);
  const steps: { key: string; content: ReactNode }[] = [];
  if (state.shareId && replacements)
    steps.push({
      key: "rest",
      content: <RestPanel id={state.shareId} count={replacements} />,
    });
  if (state.shareId && living)
    steps.push({
      key: "preserve",
      content: <PreservePanel id={state.shareId} living={living} />,
    });
  if (state.shareId)
    steps.push({ key: "share", content: <ShareLink id={state.shareId} /> });
  if (steps.length === 0) return null;

  return (
    <section
      aria-labelledby="nextTitle"
      className="mt-16 border-t border-veil pt-10"
    >
      <h3 id="nextTitle" className="font-display text-[1.75rem] text-bone">
        {t.nextTitle}
      </h3>
      <ol className="mt-8 grid gap-10 md:grid-cols-2 xl:grid-cols-3">
        {steps.map(({ key, content }, index) => (
          <li key={key} className="grid grid-cols-[2rem_1fr] gap-4">
            <span
              aria-hidden
              className="font-display text-[1.9rem] leading-none text-marigold"
            >
              {index + 1}
            </span>
            <div className="min-w-0">{content}</div>
          </li>
        ))}
      </ol>
    </section>
  );
}
