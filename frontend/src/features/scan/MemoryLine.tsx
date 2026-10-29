import { useTranslation } from "../i18n/useTranslation";
import type { Memory } from "./scanTypes";

type MemoryLineProps = { memory?: Memory; remembering: boolean };

function formatDate(isoDate: string, language: string): string {
  return new Intl.DateTimeFormat(language, {
    dateStyle: "long",
    timeZone: "UTC",
  }).format(new Date(`${isoDate}T00:00:00Z`));
}

export default function MemoryLine({ memory, remembering }: MemoryLineProps) {
  const { t, language } = useTranslation();

  if (!memory) {
    return remembering ? (
      <p className="memory-searching text-dusk">{t.memorySearching}</p>
    ) : null;
  }

  if (memory.status !== "found") {
    return (
      <p className="text-dusk">
        {memory.status === "missing" ? t.memoryMissing : t.memoryUnavailable}
      </p>
    );
  }

  return (
    <div>
      <a
        href={memory.archived_url}
        rel="noopener noreferrer"
        target="_blank"
        className="font-semibold text-spectral underline decoration-spectral/40 underline-offset-4 hover:decoration-spectral"
      >
        {t.memoryFound(formatDate(memory.captured_on, language))}
      </a>
      {memory.title ? <p className="mt-1 text-bone">{memory.title}</p> : null}
      {memory.excerpt ? (
        <p className="mt-1 max-w-[65ch] leading-[1.6] text-dusk">
          {memory.excerpt}
        </p>
      ) : null}
    </div>
  );
}
