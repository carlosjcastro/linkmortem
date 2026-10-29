import type {
  Afterlife,
  Coverage,
  Diagnosis,
  Memory,
  ScanEvent,
} from "./scanTypes";

export type ScanPhase =
  "idle" | "loading" | "collecting" | "checking" | "done" | "failed";

export type ScanState = {
  phase: ScanPhase;
  target: string;
  total: number;
  coverage: Coverage;
  results: Diagnosis[];
  memories: Record<string, Memory>;
  afterlives: Record<string, Afterlife>;
  reincarnation: boolean;
  shareId: string;
  errorCode: string;
};

export const INITIAL_SCAN: ScanState = {
  phase: "idle",
  target: "",
  total: 0,
  coverage: { found: 0, read: 0, available: 0, source: "" },
  results: [],
  memories: {},
  afterlives: {},
  reincarnation: false,
  shareId: "",
  errorCode: "",
};

export function applyEvent(state: ScanState, event: ScanEvent): ScanState {
  switch (event.type) {
    case "collected":
      return {
        ...state,
        phase: "checking",
        total: event.total,
        reincarnation: event.reincarnation,
        coverage: {
          found: event.found ?? event.total,
          read: event.read ?? 0,
          available: event.available ?? 0,
          source: event.source ?? "",
        },
      };
    case "link":
      return { ...state, results: [...state.results, event.diagnosis] };
    case "memory":
      return {
        ...state,
        memories: { ...state.memories, [event.url]: event.memory },
      };
    case "afterlife":
      return {
        ...state,
        afterlives: { ...state.afterlives, [event.url]: event.afterlife },
      };
    case "saved":
      return { ...state, shareId: event.id };
    case "done":
      return { ...state, phase: "done" };
    case "error":
      return { ...state, phase: "failed", errorCode: event.code };
  }
}
