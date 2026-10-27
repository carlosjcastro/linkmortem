import { useTranslation } from "../i18n/useTranslation";
import type { Afterlife } from "./scanTypes";

type AfterlifeLineProps = { afterlife?: Afterlife; seeking: boolean };

export default function AfterlifeLine({ afterlife, seeking }: AfterlifeLineProps) {
  const { t } = useTranslation();

  if (!afterlife) {
    return seeking ? <p className="memory-searching mt-3 text-[0.95rem] text-dusk">{t.afterlifeSearching}</p> : null;
  }

  if (afterlife.status !== "found") {
    const notes = { none: t.afterlifeNone, unavailable: t.afterlifeUnavailable, skipped: t.afterlifeSkipped };
    return <p className="mt-3 text-[0.95rem] text-dusk">{notes[afterlife.status]}</p>;
  }

  return (
    <div className="mt-3 border-l-2 border-marigold/60 pl-4">
      <p className="font-semibold text-marigold">{afterlife.match === "same" ? t.afterlifeSame : t.afterlifeSuccessor}</p>
      <a
        href={afterlife.url}
        rel="noopener noreferrer"
        target="_blank"
        className="mt-1 inline-block break-all text-bone underline decoration-marigold/40 underline-offset-4 hover:decoration-marigold"
      >
        {afterlife.title || afterlife.url}
      </a>
      {afterlife.title ? <p className="mt-1 break-all text-[0.9rem] text-dusk">{afterlife.url}</p> : null}
      {afterlife.evidence ? <p className="mt-1 max-w-[65ch] leading-[1.6] text-dusk">"{afterlife.evidence}"</p> : null}
    </div>
  );
}
