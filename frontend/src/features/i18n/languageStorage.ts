import { readValue, writeValue } from "../../lib/storage";
import type { Language } from "./dictionaries";

const STORAGE_KEY = "linkmortem.language";

export function initialLanguage(): Language {
  const saved = readValue(STORAGE_KEY);
  if (saved === "en" || saved === "es") return saved;
  return navigator.language.toLowerCase().startsWith("es") ? "es" : "en";
}

export function saveLanguage(language: Language): void {
  writeValue(STORAGE_KEY, language);
}
