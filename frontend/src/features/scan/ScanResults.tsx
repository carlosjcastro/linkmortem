import { useEffect, useRef } from "react";
import Aftercare from "../aftercare/Aftercare";
import { useTranslation } from "../i18n/useTranslation";
import { groupResults } from "./groupResults";
import ResultGroup from "./ResultGroup";
import ModelNotice from "./ModelNotice";
import ScanProgress from "./ScanProgress";
import ShareLink from "./ShareLink";
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
    <section aria-labelledby="resultsTitle" className="mx-auto w-full max-w-7xl scroll-mt-8 px-5 pb-20 pt-4 sm:px-10">
      <h2 id="resultsTitle" ref={heading} tabIndex={-1} className="max-w-[20ch] font-display text-[clamp(2rem,4vw,3.2rem)] leading-[1.05] outline-none">
        {state.phase === "done" ? t.resultsDone(groups.ghost.length) : t.resultsTitle}
      </h2>
      <p className="mt-3 break-all text-dusk">{state.target}</p>
      {running ? <ScanProgress state={state} /> : null}
      {state.phase === "done" && state.shareId ? <ShareLink id={state.shareId} /> : null}
      {state.phase === "done" ? <ModelNotice results={state.results} /> : null}
      {state.phase === "done" ? <Aftercare state={state} /> : null}
      {state.phase === "failed" ? (
        <p role="alert" className="mt-8 max-w-xl text-rose">
          {t.scanErrors[state.errorCode] ?? t.scanErrors.unavailable}
        </p>
      ) : null}
      <ResultGroup title={t.ghostsTitle} results={groups.ghost} memories={state.memories} afterlives={state.afterlives} reincarnation={state.reincarnation} remembering={running} />
      <ResultGroup title={t.unknownTitle} results={groups.unknown} />
      <ResultGroup title={t.aliveTitle} results={groups.alive} collapsed />
    </section>
  );
}
