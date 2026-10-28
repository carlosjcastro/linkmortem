import { useTranslation } from "../i18n/useTranslation";

type RestPanelProps = { id: string; count: number };

export default function RestPanel({ id, count }: RestPanelProps) {
  const { t } = useTranslation();

  return (
    <div className="max-w-2xl">
      <p className="font-semibold text-bone">{t.restTitle}</p>
      <p className="mt-1 text-[0.95rem] leading-[1.6] text-dusk">{t.restText(count)}</p>
      <a
        href={`/api/scans/${id}/patch`}
        download="linkmortem.patch"
        className="mt-3 inline-block rounded-full bg-marigold px-5 py-2 font-semibold text-night hover:brightness-110 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-bone"
      >
        {t.restDownload}
      </a>
      <p className="mt-2 text-[0.9rem] text-dusk">
        {t.restApply} <code className="rounded bg-veil px-1.5 py-0.5 text-bone">git apply linkmortem.patch</code>
      </p>
    </div>
  );
}
