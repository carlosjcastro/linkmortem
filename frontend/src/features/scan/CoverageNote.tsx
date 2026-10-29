import { useTranslation } from "../i18n/useTranslation";
import type { Coverage } from "./scanTypes";

export default function CoverageNote({
  total,
  coverage,
}: {
  total: number;
  coverage: Coverage;
}) {
  const { t } = useTranslation();
  const notes = [
    coverage.found > total ? t.coverageLinks(total, coverage.found) : "",
    coverage.available > coverage.read
      ? t.coverageSources(
          coverage.read,
          coverage.available,
          coverage.source === "repository",
        )
      : "",
  ].filter(Boolean);
  if (notes.length === 0) return null;
  return (
    <p className="mt-4 max-w-xl leading-[1.65] text-dusk">{notes.join(" ")}</p>
  );
}
