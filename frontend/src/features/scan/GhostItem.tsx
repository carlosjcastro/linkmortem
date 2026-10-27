import { useTranslation } from "../i18n/useTranslation";
import MemoryLine from "./MemoryLine";
import type { Diagnosis, Memory } from "./scanTypes";

const TONES = { ghost: "bg-rose", unknown: "bg-marigold", alive: "bg-spectral" } as const;

type GhostItemProps = { result: Diagnosis; memory?: Memory; remembering: boolean };

export default function GhostItem({ result, memory, remembering }: GhostItemProps) {
  const { t } = useTranslation();
  const dead = result.verdict === "ghost";

  return (
    <li className="grid grid-cols-[0.5rem_1fr] gap-x-5 py-5">
      <span aria-hidden className={`mt-2.5 size-2 rounded-full ${TONES[result.verdict]}`} />
      <div className="min-w-0">
        <a
          href={result.link.url}
          rel="noopener noreferrer nofollow"
          target="_blank"
          className={`break-all text-[1.05rem] text-bone underline-offset-4 hover:underline ${dead ? "line-through decoration-rose/60" : ""}`}
        >
          {result.link.url}
        </a>
        <p className="mt-1 font-semibold text-bone">
          {t.causes[result.cause]}
          {result.status_code && result.status_code >= 400 ? <span className="ml-2 font-normal text-dusk">(HTTP {result.status_code})</span> : null}
        </p>
        {result.evidence ? <p className="mt-1 max-w-[60ch] leading-[1.6] text-dusk">{result.evidence}</p> : null}
        {dead ? <MemoryLine memory={memory} remembering={remembering} /> : null}
        <p className="mt-1 text-[0.9rem] text-dusk">
          {t.foundOn}{" "}
          <a href={result.link.source} rel="noopener noreferrer" target="_blank" className="break-all underline decoration-veil underline-offset-4 hover:text-bone">
            {result.link.source}
          </a>
        </p>
      </div>
    </li>
  );
}
