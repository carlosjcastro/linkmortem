import { readLines } from "../../lib/ndjson";
import type { ScanEvent } from "./scanTypes";

const SCAN_ENDPOINT = "/api/scans/stream";

export async function* streamScan(target: string, signal: AbortSignal): AsyncGenerator<ScanEvent> {
  const response = await fetch(SCAN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target }),
    signal,
  });
  if (!response.ok || !response.body) {
    const refusal = await response.json().catch(() => ({}));
    yield { type: "error", code: refusal.code ?? "unavailable", message: refusal.message ?? "" };
    return;
  }
  for await (const line of readLines(response.body)) {
    yield JSON.parse(line) as ScanEvent;
  }
}
