import { useTranslation } from "../i18n/useTranslation";
import type { Diagnosis } from "./scanTypes";

export default function CauseLine({ result }: { result: Diagnosis }) {
  const { t } = useTranslation();

  return (
    <>
      <p className="text-bone">
        {t.causes[result.cause]}
        {result.status_code && result.status_code >= 400 ? (
          <span className="ml-2 text-dusk">(HTTP {result.status_code})</span>
        ) : null}
      </p>
      {result.evidence ? (
        <p className="mt-1 max-w-[62ch] text-dusk">{result.evidence}</p>
      ) : null}
    </>
  );
}
