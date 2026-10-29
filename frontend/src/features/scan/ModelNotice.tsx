import { useTranslation } from "../i18n/useTranslation";
import type { Diagnosis } from "./scanTypes";

export default function ModelNotice({ results }: { results: Diagnosis[] }) {
  const { t } = useTranslation();
  const missed = results.filter(
    (result) => result.cause === "model_unavailable",
  ).length;
  if (missed === 0) return null;
  return (
    <p className="mt-8 max-w-xl leading-[1.65] text-marigold">
      {t.modelMissing(missed)}
    </p>
  );
}
