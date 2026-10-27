import { useContext } from "react";
import { LanguageContext } from "./LanguageProvider";

export function useTranslation() {
  const state = useContext(LanguageContext);
  if (!state)
    throw new Error("useTranslation must be used inside LanguageProvider");
  return state;
}
