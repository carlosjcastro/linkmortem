import { createContext, useEffect, useState, type ReactNode } from "react";
import { dictionaries, type Dictionary, type Language } from "./dictionaries";
import { initialLanguage, saveLanguage } from "./languageStorage";

type LanguageState = {
  language: Language;
  t: Dictionary;
  switchLanguage: () => void;
};

export const LanguageContext = createContext<LanguageState | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState(initialLanguage);

  useEffect(() => {
    document.documentElement.lang = language;
    saveLanguage(language);
  }, [language]);

  const switchLanguage = () =>
    setLanguage((current) => (current === "en" ? "es" : "en"));

  return (
    <LanguageContext
      value={{ language, t: dictionaries[language], switchLanguage }}
    >
      {children}
    </LanguageContext>
  );
}
