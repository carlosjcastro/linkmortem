import { useTranslation } from "./useTranslation";

export default function LanguageToggle() {
  const { t, switchLanguage } = useTranslation();

  return (
    <button
      type="button"
      onClick={switchLanguage}
      aria-label={`${t.language}: ${t.otherLanguage}`}
      className="py-2 text-dusk transition-colors hover:text-bone"
    >
      {t.otherLanguage}
    </button>
  );
}
