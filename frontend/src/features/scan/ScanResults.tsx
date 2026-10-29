import { useEffect, useRef } from "react";
import NextSteps from "../aftercare/NextSteps";
import { useTranslation } from "../i18n/useTranslation";
import GhostAutopsy from "./GhostAutopsy";
import { groupResults } from "./groupResults";
import LinkItem from "./LinkItem";
import ResultGroup from "./ResultGroup";
import ResultsSummary from "./ResultsSummary";
import { SECTIONS } from "./sectionAnchors";
import type { ScanState } from "./scanState";

export default function ScanResults({ state }: { state: ScanState }) {
  const { t } = useTranslation();
  const heading = useRef<HTMLHeadingElement>(null);
  const groups = groupResults(state.results);
  const running = state.phase === "collecting" || state.phase === "checking";

  useEffect(() => {
    if (state.phase === "collecting") heading.current?.focus();
  }, [state.phase, state.target]);

  if (state.phase === "idle") return null;

  return (
    <section
      aria-labelledby="resultsTitle"
      className="mx-auto w-full max-w-7xl scroll-mt-8 px-5 pb-20 pt-4 sm:px-10"
    >
      <ResultsSummary ref={heading} state={state} groups={groups} />
      {state.phase === "failed" ? (
        <p role="alert" className="mt-8 max-w-xl text-rose">
          {t.scanErrors[state.errorCode] ?? t.scanErrors.unavailable}
        </p>
      ) : null}
      {state.phase === "done" ? <NextSteps state={state} /> : null}
      <ResultGroup
        id={SECTIONS.ghost}
        title={t.ghostsTitle}
        count={groups.ghost.length}
      >
        {groups.ghost.map((result, index) => (
          <GhostAutopsy
            key={result.link.url}
            index={index}
            result={result}
            memory={state.memories[result.link.url]}
            afterlife={state.afterlives[result.link.url]}
            reincarnation={state.reincarnation}
            remembering={running}
          />
        ))}
      </ResultGroup>
      <ResultGroup
        id={SECTIONS.unknown}
        title={t.unknownTitle}
        count={groups.unknown.length}
        hint={t.unknownHint}
        collapsed={groups.ghost.length > 0}
      >
        {groups.unknown.map((result) => (
          <LinkItem key={result.link.url} result={result} />
        ))}
      </ResultGroup>
      <ResultGroup
        id={SECTIONS.alive}
        title={t.aliveTitle}
        count={groups.alive.length}
        collapsed
      >
        {groups.alive.map((result) => (
          <LinkItem key={result.link.url} result={result} />
        ))}
      </ResultGroup>
    </section>
  );
}
