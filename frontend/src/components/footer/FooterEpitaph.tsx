import { useTranslation } from "../../features/i18n/useTranslation";
import BrandMark from "../BrandMark";

export default function FooterEpitaph() {
  const { t } = useTranslation();

  return (
    <div className="max-w-md">
      <div className="flex items-center gap-3 text-spectral">
        <BrandMark />
        <p className="text-sm font-semibold uppercase tracking-[0.2em]">
          {t.footer.memoriam}
        </p>
      </div>
      <p className="spectral-type mt-5 font-display text-2xl leading-snug text-bone sm:text-3xl">
        {t.footer.epitaph}
      </p>
      <p className="mt-4 leading-relaxed">{t.footer.note}</p>
    </div>
  );
}
