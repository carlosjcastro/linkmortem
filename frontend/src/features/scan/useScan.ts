import { useCallback, useRef, useState } from "react";
import type { Afterlife, Diagnosis, Memory } from "./scanTypes";
import { streamScan } from "./scanStream";

export type ScanPhase = "idle" | "collecting" | "checking" | "done" | "failed";

export type ScanState = {
  phase: ScanPhase;
  target: string;
  total: number;
  results: Diagnosis[];
  memories: Record<string, Memory>;
  afterlives: Record<string, Afterlife>;
  reincarnation: boolean;
  errorCode: string;
};

const INITIAL: ScanState = { phase: "idle", target: "", total: 0, results: [], memories: {}, afterlives: {}, reincarnation: false, errorCode: "" };

export function useScan() {
  const [state, setState] = useState<ScanState>(INITIAL);
  const controller = useRef<AbortController | null>(null);

  const start = useCallback(async (target: string) => {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setState({ ...INITIAL, phase: "collecting", target });
    try {
      for await (const event of streamScan(target, current.signal)) {
        if (event.type === "collected") setState((previous) => ({ ...previous, phase: "checking", total: event.total, reincarnation: event.reincarnation }));
        if (event.type === "link") setState((previous) => ({ ...previous, results: [...previous.results, event.diagnosis] }));
        if (event.type === "memory") setState((previous) => ({ ...previous, memories: { ...previous.memories, [event.url]: event.memory } }));
        if (event.type === "afterlife") setState((previous) => ({ ...previous, afterlives: { ...previous.afterlives, [event.url]: event.afterlife } }));
        if (event.type === "done") setState((previous) => ({ ...previous, phase: "done" }));
        if (event.type === "error") setState((previous) => ({ ...previous, phase: "failed", errorCode: event.code }));
      }
    } catch {
      if (!current.signal.aborted) setState((previous) => ({ ...previous, phase: "failed", errorCode: "unavailable" }));
    }
  }, []);

  return { state, start };
}
