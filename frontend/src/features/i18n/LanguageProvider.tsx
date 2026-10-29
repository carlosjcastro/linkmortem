import { createContext, useEffect, useState, type ReactNode } from "react";
import { dictionaries, type Dictionary, type Language } from "./dictionaries";

const FIRST_LANGUAGE: Language = "en";

type LanguageState = {
  language: Language;
  t: Dictionary;
  chooseLanguage: (language: Language) => void;
};

export const LanguageContext = createContext<LanguageState | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, chooseLanguage] = useState<Language>(FIRST_LANGUAGE);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  return (
    <LanguageContext
      value={{ language, t: dictionaries[language], chooseLanguage }}
    >
      {children}
    </LanguageContext>
  );
}
