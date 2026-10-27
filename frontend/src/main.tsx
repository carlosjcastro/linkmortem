import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { LanguageProvider } from "./features/i18n/LanguageProvider";
import { MotionProvider } from "./features/motion/MotionProvider";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LanguageProvider>
      <MotionProvider>
        <App />
      </MotionProvider>
    </LanguageProvider>
  </StrictMode>,
);
