import type { Language } from "./dictionaries";
import { useTranslation } from "./useTranslation";

const LANGUAGES: { code: Language; name: string }[] = [
  { code: "en", name: "English" },
  { code: "es", name: "Español" },
];

export default function LanguageToggle() {
  const { t, language, chooseLanguage } = useTranslation();

  return (
    <div role="group" aria-label={t.language} className="flex items-center">
      {LANGUAGES.map(({ code, name }) => (
        <button
          key={code}
          type="button"
          lang={code}
          aria-label={name}
          aria-pressed={language === code}
          onClick={() => chooseLanguage(code)}
          className={`px-1.5 py-2 text-sm sm:px-2 font-semibold uppercase tracking-[0.14em] underline-offset-[0.6em] transition-colors ${language === code ? "text-bone underline decoration-marigold decoration-2" : "text-dusk hover:text-bone"}`}
        >
          {code}
        </button>
      ))}
    </div>
  );
}
