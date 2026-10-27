import { createContext, useEffect, useState, type ReactNode } from "react";
import { initialMotion, saveMotion } from "./motionStorage";

type MotionState = { enabled: boolean; toggle: () => void };

export const MotionContext = createContext<MotionState | null>(null);

export function MotionProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabled] = useState(initialMotion);

  useEffect(() => {
    document.documentElement.dataset.motion = enabled ? "on" : "off";
    saveMotion(enabled);
  }, [enabled]);

  const toggle = () => setEnabled((current) => !current);

  return <MotionContext value={{ enabled, toggle }}>{children}</MotionContext>;
}
