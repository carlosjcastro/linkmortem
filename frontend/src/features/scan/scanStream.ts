import { postNdjson } from "../../lib/postNdjson";
import type { ScanEvent } from "./scanTypes";

const SCAN_ENDPOINT = "/api/scans/stream";

export function streamScan(target: string, signal: AbortSignal): AsyncGenerator<ScanEvent> {
  return postNdjson<ScanEvent>(SCAN_ENDPOINT, { target }, signal);
}
