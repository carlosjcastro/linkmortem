import { useTranslation } from "../features/i18n/useTranslation";
import type { CopyStatus } from "../lib/useCopy";

type CopyStatusNoteProps = { status: CopyStatus; copied: string };

export default function CopyStatusNote({
  status,
  copied,
}: CopyStatusNoteProps) {
  const { t } = useTranslation();

  if (status === "failed") {
    return (
      <p role="alert" className="mt-2 text-[0.9rem] text-rose">
        {t.copyFailed}
      </p>
    );
  }
  return (
    <span aria-live="polite" className="sr-only">
      {status === "copied" ? copied : ""}
    </span>
  );
}
