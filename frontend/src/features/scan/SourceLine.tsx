import { useTranslation } from "../i18n/useTranslation";

export default function SourceLine({ source }: { source: string }) {
  const { t } = useTranslation();

  return (
    <p className="mt-1 text-[0.9rem] text-dusk">
      {t.foundOn}{" "}
      <a
        href={source}
        rel="noopener noreferrer"
        target="_blank"
        className="break-all underline decoration-veil underline-offset-4 hover:text-bone"
      >
        {source}
      </a>
    </p>
  );
}
