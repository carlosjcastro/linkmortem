import { useEffect, useState } from "react";

export type CopyStatus = "idle" | "copied" | "failed";

const RESET_MS = 2500;

export function useCopy(text: string) {
  const [status, setStatus] = useState<CopyStatus>("idle");

  useEffect(() => {
    if (status !== "copied") return;
    const timer = window.setTimeout(() => setStatus("idle"), RESET_MS);
    return () => window.clearTimeout(timer);
  }, [status]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setStatus("copied");
    } catch {
      setStatus("failed");
    }
  };

  return { status, copy };
}
