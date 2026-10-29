import type { Ref } from "react";
import HauntedHouse from "../house/HauntedHouse";
import { useTranslation } from "../i18n/useTranslation";
import CoverageNote from "./CoverageNote";
import ModelNotice from "./ModelNotice";
import ScanProgress from "./ScanProgress";
import type { ScanState } from "./scanState";
import type { Diagnosis, Verdict } from "./scanTypes";
import Tally from "./Tally";

type ResultsSummaryProps = {
  state: ScanState;
  groups: Record<Verdict, Diagnosis[]>;
  ref: Ref<HTMLHeadingElement>;
};

export default function ResultsSummary({
  state,
  groups,
  ref,
}: ResultsSummaryProps) {
  const { t } = useTranslation();
  const running = state.phase === "collecting" || state.phase === "checking";
  const done = state.phase === "done";
  const title = done
    ? t.resultsDone(groups.ghost.length)
    : state.phase === "failed"
      ? t.resultsFailed
      : t.resultsTitle;

  return (
    <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:gap-14">
      <div className="min-w-0">
        <h2
          id="resultsTitle"
          ref={ref}
          tabIndex={-1}
          className="max-w-[18ch] font-display text-[clamp(2.1rem,4.2vw,3.4rem)] leading-[1.05] outline-none"
        >
          {title}
        </h2>
        <p className="mt-3 break-all text-dusk">{state.target}</p>
        {running ? <ScanProgress state={state} /> : null}
        {done ? <Tally groups={groups} /> : null}
        {done ? (
          <CoverageNote total={state.total} coverage={state.coverage} />
        ) : null}
        {done ? <ModelNotice results={state.results} /> : null}
      </div>
      {done && state.results.length ? (
        <HauntedHouse
          alive={groups.alive.length}
          ghost={groups.ghost.length}
          unknown={groups.unknown.length}
          ghostUrls={groups.ghost.map((result) => result.link.url)}
        />
      ) : null}
    </div>
  );
}
