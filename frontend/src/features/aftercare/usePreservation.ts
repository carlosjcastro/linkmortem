import { useCallback, useState } from "react";
import { streamPreservation } from "./preserveStream";

export type Preservation = {
  phase: "idle" | "running" | "done" | "failed";
  total: number;
  saved: { url: string; status: "queued" | "failed"; detail: string }[];
  errorCode: string;
};

const IDLE: Preservation = { phase: "idle", total: 0, saved: [], errorCode: "" };

export function usePreservation(id: string) {
  const [state, setState] = useState<Preservation>(IDLE);

  const start = useCallback(async () => {
    setState({ ...IDLE, phase: "running" });
    try {
      for await (const event of streamPreservation(id, new AbortController().signal)) {
        if (event.type === "preserving") setState((previous) => ({ ...previous, total: event.total }));
        if (event.type === "preserved") setState((previous) => ({ ...previous, saved: [...previous.saved, { url: event.url, status: event.status, detail: event.detail }] }));
        if (event.type === "done") setState((previous) => ({ ...previous, phase: "done" }));
        if (event.type === "error") setState((previous) => ({ ...previous, phase: "failed", errorCode: event.code }));
      }
    } catch {
      setState((previous) => ({ ...previous, phase: "failed", errorCode: "unavailable" }));
    }
  }, [id]);

  return { state, start };
}
