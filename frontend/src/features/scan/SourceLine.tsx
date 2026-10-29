import { useTranslation } from "../i18n/useTranslation";
import type { Diagnosis } from "./scanTypes";
import { sourceLabel } from "./sourceLabel";
import { externalHref } from "../../lib/externalHref";

const SHOWN_SOURCES = 3;

export default function SourceLine({ link }: { link: Diagnosis["link"] }) {
  const { t } = useTranslation();
  const sources = [link.source, ...(link.other_sources ?? [])];
  const hidden = sources.length - SHOWN_SOURCES;

  return (
    <p className="mt-1 text-[0.9rem] text-dusk">
      {t.foundOn}{" "}
      {sources.slice(0, SHOWN_SOURCES).map((source, index) => (
        <span key={source}>
          {index > 0 ? ", " : null}
          <a
            href={externalHref(source)}
            rel="noopener noreferrer"
            target="_blank"
            className="break-all underline decoration-veil underline-offset-4 hover:text-bone"
          >
            {sourceLabel(source)}
          </a>
        </span>
      ))}
      {hidden > 0 ? ` ${t.moreSources(hidden)}` : null}
    </p>
  );
}
