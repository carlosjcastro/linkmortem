import { useCallback, useRef, useState } from "react";
import { fetchSavedScan } from "./savedScan";
import { applyEvent, INITIAL_SCAN, type ScanState } from "./scanState";
import { streamScan } from "./scanStream";

export type { ScanPhase, ScanState } from "./scanState";

export function useScan() {
  const [state, setState] = useState<ScanState>(INITIAL_SCAN);
  const controller = useRef<AbortController | null>(null);

  const renew = useCallback(() => {
    controller.current?.abort();
    controller.current = new AbortController();
    return controller.current;
  }, []);

  const start = useCallback(
    async (target: string) => {
      const current = renew();
      setState({ ...INITIAL_SCAN, phase: "collecting", target });
      try {
        for await (const event of streamScan(target, current.signal)) {
          setState((previous) => applyEvent(previous, event));
        }
      } catch {
        if (!current.signal.aborted) setState((previous) => ({ ...previous, phase: "failed", errorCode: "unavailable" }));
      }
    },
    [renew],
  );

  const load = useCallback(
    async (id: string) => {
      const current = renew();
      setState({ ...INITIAL_SCAN, phase: "collecting" });
      try {
        const saved = await fetchSavedScan(id, current.signal);
        if (!saved) {
          setState({ ...INITIAL_SCAN, phase: "failed", errorCode: "scan_not_found" });
          return;
        }
        const replayed = saved.events.reduce(applyEvent, { ...INITIAL_SCAN, target: saved.target });
        setState({ ...replayed, shareId: id });
      } catch {
        if (!current.signal.aborted) setState({ ...INITIAL_SCAN, phase: "failed", errorCode: "unavailable" });
      }
    },
    [renew],
  );

  return { state, start, load };
}
