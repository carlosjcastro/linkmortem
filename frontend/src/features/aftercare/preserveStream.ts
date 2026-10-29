import { postNdjson } from "../../lib/postNdjson";

export type PreserveEvent =
  | { type: "preserving"; total: number }
  | { type: "waiting"; seconds: number }
  | {
      type: "preserved";
      url: string;
      status: "queued" | "recent" | "failed";
      detail: string;
    }
  | { type: "done" }
  | { type: "error"; code: string; message: string };

export function streamPreservation(
  id: string,
  signal: AbortSignal,
): AsyncGenerator<PreserveEvent> {
  return postNdjson<PreserveEvent>(`/api/scans/${id}/preserve`, {}, signal);
}
